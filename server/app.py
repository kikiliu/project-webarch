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
        if user_set_alias and (db_alias.get(str(user_set_alias)) is None):  # if user sets alias AND the alias is not in current db, assgin the alias
            alias = str(user_set_alias)
        else:                                                               # if user-set alias is in current db or user doesn't set any alias, assign a random alias
            alias = random_alias()
        db_url[url] = alias
        db_alias[alias] = url
        db_alias.sync()
        db_url.sync()
    return alias

def generate_user_id():
                                                                            #in shelves, key has to be string type
    if len(db_history) == 0:
        user_id = '0'
    else:
        current_largest_id = max(db_history.keys())
        app.logger.debug("user id is" + current_largest_id)
        user_id = int(current_largest_id) + 1
    return str(user_id)

def parse_title(url):
    """Input: url string; Output:html data string"""
 
    soup = BeautifulSoup(urlopen(url))
    title = soup.head.title

    if title is None:
        title = "Page not found"
    else:
        title = title.get_text()
    return title

# class UrlHistory():
#     """Used to store each url information under each user id"""
#     def __init__(self, title, alias, date, note):
#         self.title = title
#         self.alias = alias
#         self.date = date
#         self.note = note        

def get_history(user_id):
    """Gets the user_id from the cookie and renders title, alias, date, 
    and comments and returns as text"""
    history_title = "<h2 class='form-signin-heading'>Links You Have Recently Shortened (up to 10 links)</h2>"
    history_result = ""
    history_list = db_history.get(user_id)

    if history_list:
        list_length = len(history_list)
        for value in history_list[-1:-min(list_length,10)-1:-1]:
            app.logger.debug(value)
            history_result += ("<div class='form-signin form-history'><div id='url_title'><span class='history-info-title'>" + value[0] 
                    + "</span><br /></div><div class='form-signin form-history'><div id='history_url_only'><span>http://people.ischool.berkeley.edu/~kikiliu/short/" + value[1] 
                    + "</span></div></div><div id='url_note'><span class='history-note'>"
                    + value[3] + "</span></div><div id='time_stamp'><span>" + value[2] + "</span><input type='button' class='btn btn-small btn-primary copybtn-xsmall copybutton' data-clipboard-text= 'http://people.ischool.berkeley.edu/~kikiliu/server/short/"
                    + value[1] + "' value='Copy'/></div></div>")
    if history_result == "":
        data = history_title + "<div class='form-signin form-history'><span class='history-info-title'>Sorry, no you don't have history yet.</span></div>"
    else:
        data = history_title + history_result
    return data
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
            display_style='display:none')
    resp = flask.make_response(html_file)

    user_id = flask.request.cookies.get('user_id')
    if user_id is None:
        user_id = generate_user_id()                                  
        expiresTime = datetime.datetime.now() + datetime.timedelta(days = 365)
        resp.set_cookie('user_id', user_id, expires=expiresTime, path='/~kikiliu/server')
    return resp


@app.route("/shorts", methods=['PUT', 'POST'])
def shorts_post():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    user_id = flask.request.cookies.get('user_id')
    if user_id is None:
        user_id = generate_user_id()
    user_id = str(user_id)
    app.logger.debug("Current user id is" + user_id)
    history_data = get_history(user_id)

    url = str(flask.request.form.get('url'))
    alias = generate_alias(url)
    title = parse_title(url)

    note = str(flask.request.form.get('note'))
    date = time.strftime("%d/%m/%Y %H:%M:%S")

    tuple_new = (title, alias, date, note)
    list_hist = db_history.get(user_id)

    if list_hist is None:
        db_history[user_id]= [tuple_new]
    else:
        db_history[user_id].append(tuple_new)
    db_history.sync()                                           #sync shelves whenever it is changed
 
    app.logger.debug('alias = ' + alias + '; url = ' + url)

    html_file = flask.render_template(
                'home.html',
                alias=alias,
                display_style='display:block',
                history_list = history_data)
    resp = flask.make_response(html_file)
    expiresTime = datetime.datetime.now() + datetime.timedelta(days = 365)
    resp.set_cookie('user_id', user_id, expires=expiresTime, path='/~kikiliu/server')
    return resp

@app.route('/short/<alias>', methods=['GET'])
def short_get(alias):                                           #local variable get from url
    """Redirects to original url."""
    alias = str(alias)
    destination = db_alias.get(alias)
    if destination:
        app.logger.debug("Redirecting to " + destination)
        return flask.redirect(destination)
    else:
        return flask.render_template('page_not_found.html'), 404

def highlight_note(match_obj):  

    return "<span class='highlight'>" + match_obj.group(0) + "</span>"

@app.route("/search", methods=['PUT', 'POST'])
def search_get():
    """Gets the user_id from the cookie and the word from the
    text box, and searches the user db for the matching comments. 
    Once it has all the details, it will render title, alias, date, 
    and comments and returns as text"""
    search_title = "<h2 class='form-signin-heading'>Search Result</h2>"
    search_result = ""
    user_id = str(flask.request.cookies.get('user_id'))
    search_word = str(flask.request.form.get('search_term'))

    regex = re.compile("|".join(search_word.lower().split()), flags=re.IGNORECASE)
    history_list = db_history.get(user_id)
    if history_list:
        for value in history_list:
            app.logger.debug(value)
            if regex.search(value[3].lower()):
                highlight_text = regex.sub(highlight_note, value[3])
                search_result += ("<div class='form-signin form-history'><div id='url_title'><span class='history-info-title'>" + value[0] 
                    + "</span><br /></div><div class='form-signin form-history'><div id='history_url_only'><span>http://people.ischool.berkeley.edu/~kikiliu/short/" + value[1] 
                    + "</span></div></div><div id='url_note'><span class='history-note'>"
                    + highlight_text + "</span></div><div id='time_stamp'><span>" + value[2] + "</span><input type='button' class='btn btn-small btn-primary copybtn-xsmall copybutton' data-clipboard-text= 'http://people.ischool.berkeley.edu/~kikiliu/server/short/"
                    + value[1] + "' value='Copy'/></div></div>")
                # <input type='button' class='btn btn-small btn-primary copybtn-xsmall copybutton' data-clipboard-text=" + "http://people.ischool.berkeley.edu/~kikiliu/server/short/" + value[1] + " value='Copy'/>
    if search_result == "":
        data = search_title + "<div class='form-signin form-history'><span class='history-info-title'>Sorry, no result found.</span></div>"
    else:
        data = search_title + search_result
    return flask.jsonify(result=data)

if __name__ == "__main__":
	# app.debug = True
    app.run(port=int(environ['FLASK_PORT']))