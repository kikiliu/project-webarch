#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ
from random import choice
from string import ascii_letters, digits
import datetime

app = flask.Flask(__name__)
app.debug = True

"""key is alias, value is URL, db_alias stands for shorten.db ()"""
db_alias = shelve.open("shorten.db")

"""key is url, value is alias"""
db_url = shelve.open("url.db")

"""key is user id, value is list of tuples, maintaining chronological order???"""
history = shelve.open("user.db")


def maintain_history(datetime, user, title, alias, note): #to Rahul, this is a function to manipulate history section
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
           'home.html',
            display_style='display:none',
            display_history='display:none')
    resp = flask.make_response(html_file)

    user_id = request.cookies.get('user_id')
    if user_id is None:
        user_id = generate_user_id()
        expiresTime = datetime.datetime.now() + datetime.timedelta(days = 365)
        resp.set_cookie('user_id', user_id, expires=expireTime, path='/~kikiliu/server')
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
 
    app.logger.debug('alias = ' + alias + ' url = ' + url)
    return flask.render_template(
        'home.html',
        alias=alias,
        display_style=''
        display_history='')


@app.route('/short/<alias>', methods=['GET'])
def short_get(alias):
    """Redirects to original url."""
    alias = alias.encode('ascii','ignore')
    destination = db.get(alias)
    if destination:
        app.logger.debug("Redirecting to " + destination)
        return flask.redirect(destination)
    else:
        return flask.render_template('page_not_found.html'), 404


if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))
