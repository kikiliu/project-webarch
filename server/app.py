import shelve
from subprocess import check_output
import flask
#Added by Rahul
from flask import request, jsonify
#modification ends here
from os import environ
from random import choice
from string import ascii_letters, digits
import datetime
#Added by Rahul-----------------------------------------------------------------------------------------------
import time
from bs4 import BeautifulSoup
import urllib2
import re
#modification ends here---------------------------------------------------------------------------------------

app = flask.Flask(__name__)
app.debug = True
user_id = 1

"""key is alias, value is URL, db_alias stands for shorten.db ()"""
db_alias = shelve.open("shorten.db")

"""key is url, value is alias"""
db_url = shelve.open("url.db")

"""key is user id, value is list of tuples, maintaining chronological order???"""
#Name modified by Rahul---------------------------------------------------------------------------------------
db_history = shelve.open("user.db")
#modification ends here---------------------------------------------------------------------------------------


def maintain_history(datetime, user, title, alias, note):
	 #to Rahul, this is a function to manipulate history section
    pass


def random_alias():
    while True:        
        alias = ''.join([choice(ascii_letters + digits) for i in range(7)]) # Get 7 random letter/digit combination
                                                                            # the length of alias is adopted from bitly
        if db_alias.get(alias) is None:
            return alias

def generate_user_id(current_largest_id):
    current_largest_id += 1
    return user_id

###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/home', methods=['GET'])
def home():
    """Builds a template based on a GET request, with some default
    arguements"""

    html_file = flask.render_template(
           'Test.html',
            display_style='display:none',
            display_history='display:none')
    resp = flask.make_response(html_file)

    user_id = request.cookies.get('user_id')
    if user_id is None:
        user_id = generate_user_id(11111)
        expiresTime = datetime.datetime.now() + datetime.timedelta(days = 365)
        resp.set_cookie('user_id', user_id, expires=expiresTime, path='/')
    return resp


@app.route("/shorts", methods=['PUT', 'POST'])
def shorts_post():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    url = request.form.get('url')
    
    alias = db_url.get(url)
    if alias is None:                                                       # if url in not in current db, try to get user-specified alias or random alias
        user_set_alias = request.form.get('alias').encode('ascii', 'ignore')
        if user_set_alias and db_alias.get(alias) is None:                  # if user sets alias AND the alias is not in current db, assgin the alias
            alias = user_set_alias
        else:                                                               # if user-set alias is in current db or user doesn't set any alias, assign a random alias
            alias = random_alias()

        db_url[url] = alias
        db_alias[alias] = url

#Added by Rahul----------------------------------------------------------------------------------------------
    cookie_id = request.cookies.get('user_id')
    soup = BeautifulSoup(urllib2.urlopen(url))
    title = soup.title.string
    comments = request.form.get('comment_word')
    date = time.strftime("%d/%m/%Y %H:%M:%S")
    tuple_new = (title,url,date,comments)
    tuple_hist = db_history.get(cookie_id)
    if tuple_hist == None:
        db_history[cookie_id] = [tuple_new]
    else:
        tuple_hist.append(tuple_new)
	 db_history[cookie_id] = tuple_hist
#modification ends here---------------------------------------------------------------------------------------
 
    app.logger.debug('alias = ' + alias + ' url = ' + url)
#    return flask.render_template(							# Rahul: Please uncheck the comments. I had commented them as I was facing some issue running app.py
#        'home.html',
#        alias=alias,
#        display_style=''
#        display_history='')

#Added by Rahul----------------------------------------------------------------------------------------------
@app.route("/history", methods=['PUT', 'POST'])
def history_get():
    """Gets the userid from the cookie and the word from the
    text box and searches the user db for the matching comments. Once it has all
    the details, it will create a li with title, alias, date, and comments and
    return as text"""
    cookie_userid = request.cookies.get('user_id')
    search_word = request.form.get('comment_word')
    history_tuple = db_history.get(cookie_userid)
    data = ''
    regex = re.compile("|".join(string.lower().split()))
    history_list = db_history.get(userid)
    for index,value in enumerate(history_list):
        if regex.search(value[3].lower()):
            data += "<li><span class=history_section><a href=" + value[0] + ">" + value[0] + "</a>, " + value[1] + ", " + value[2] + "<span class=comment_section>" + value[3] + "</span></span></li>"
    if data == '':
        data = '<li><span class=history_section>No match found</span></li>'
    return jsonify(result=data)
#modification ends here---------------------------------------------------------------------------------------


if __name__ == "__main__":
	app.debug = True
    	app.run(port=int(environ['FLASK_PORT']))
