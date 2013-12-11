import shelve
from subprocess import check_output
import flask
#Merged with flask module above
# from flask import request, jsonify
from os import environ
from random import choice
from string import ascii_letters, digits
import datetime
import time
from bs4 import BeautifulSoup
from urllib2 import urlopen
import re

app = flask.Flask(__name__)
app.debug = True
user_id = 1

"""key is alias, value is URL, db_alias stands for shorten.db"""
db_alias = shelve.open("shorten.db", writeback=True)

"""key is url, value is alias"""
db_url = shelve.open("url.db", writeback=True)

"""key is user id, value is list of tuples used to store the user's history"""
db_history = shelve.open("user.db", writeback=True)

# def maintain_history(datetime, user, title, alias, note):
# 	 #to Rahul, this is a function to manipulate history section
#     pass


def random_alias():
    """ Gets 7 random letter/digit combination
    The length of alias is adopted from bitly"""
    while True:        
        alias = ''.join([choice(ascii_letters + digits) for i in range(7)])
        if db_alias.get(alias) is None:
            return alias

def generate_alias(url):
    """Generates alias for long url and store the alias in db_alias and db_url"""
    alias = db_url.get(url)
    if alias is None:                                                       # if url in not in current db, try to get user-specified alias or random alias
        user_set_alias = flask.request.form.get('alias')
        if user_set_alias and (db_alias.get(str(user_set_alias)) is None):                 # if user sets alias AND the alias is not in current db, assgin the alias
            alias = str(user_set_alias)
        else:                                                               # if user-set alias is in current db or user doesn't set any alias, assign a random alias
            alias = random_alias()
        db_url[url] = alias
        db_alias[alias] = url
        db_alias.sync()
        db_url.sync()
    return alias

def generate_user_id():
    if len(db_history) == 0:
        user_id = 0
    else:
        current_largest_id = max(db_history.keys())
        user_id = current_largest_id + 1
    return user_id

def parse_title(url):
    """Input: url string; Output:html data string"""
    response = urlopen(url) 
    data = response.read()
    title = BeautifulSoup(data).head.title.get_text()
    if title is None:
        title = "Page not found"
    return title

# class UrlHistory():
#     """Used to store each url information under each user id"""
#     def __init__(self, title, alias, date, note):
#         self.title = title
#         self.alias = alias
#         self.date = date
#         self.note = note        

###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/home', methods=['GET'])
def home():
    """Builds a template based on a GET request, with some default
    arguements"""
    html_file = flask.render_template(
           'home.html',
            display_style='display:none',
            display_history='display:none')
    resp = flask.make_response(html_file)

    user_id = flask.request.cookies.get('user_id')
    if user_id is None:
        user_id = generate_user_id()                                  
        expiresTime = datetime.datetime.now() + datetime.timedelta(days = 365)
        resp.set_cookie('user_id', user_id, expires=expiresTime, path='/~kikiliu/server') #which path???
    return resp


@app.route("/shorts", methods=['PUT', 'POST'])
def shorts_post():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    url = str(flask.request.form.get('url'))

    alias = generate_alias(url)
    title = parse_title(url)
    user_id = str(flask.request.cookies.get('user_id'))
    note = str(flask.request.form.get('note'))
    date = time.strftime("%d/%m/%Y %H:%M:%S")

    tuple_new = (title, alias, date, note)
    list_hist = db_history.get(user_id)
    if list_hist is None:
        db_history[user_id]=[tuple_new]
    else:
        db_history[user_id].append(tuple_new)
    db_history.sync()
 
    app.logger.debug('alias = ' + alias + '; url = ' + url)
    return flask.render_template(
       'home.html',
       alias=alias,
       display_style='block',
       display_history='block')

@app.route('/short/<alias>', methods=['GET'])
def short_get(alias):                       #local variable get from url
    """Redirects to original url."""
    alias = str(alias)
    destination = db_alias.get(alias)
    if destination:
        app.logger.debug("Redirecting to " + destination)
        return flask.redirect(destination)
    else:
        return flask.render_template('page_not_found.html'), 404


@app.route("/history", methods=['PUT', 'POST'])
def history_get():
    """Gets the user_id from the cookie and the word from the
    text box, and searches the user db for the matching comments. 
    Once it has all the details, it will create <li> tags with 
    title, alias, date, and comments and return as text"""
    data = ''

    user_id = str(flask.request.cookies.get('user_id'))
    search_word = str(flask.request.form.get('search_term'))

    regex = re.compile("|".join(search_word.lower().split()))
    history_list = db_history.get(user_id)
    if history_list:
        for value in history_list:
            #app.logger.debug(value)
            if regex.search(value[3].lower()):
                data += ("<div class='form-signin form-history'><span class='history-info-title'>" + value[0] + "</span><br /><span>http://people.ischool.berkeley.edu/~kikiliu/server/short/" + value[1] + "</span><input type='button' class='btn btn-small btn-primary copybtn-xsmall copybutton' data-clipboard-target='short_url' value='Copy'/><span class='history-info'>"
                + value[3] + "</span></div>")
    if data == "":
        data = "<div class='form-signin form-history'><span class='history-info-title'>Sorry, no result found.</span></div>"
    return flask.jsonify(result=data)

if __name__ == "__main__":
	# app.debug = True
    app.run(port=int(environ['FLASK_PORT']))