#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request
from os import environ

app = flask.Flask(__name__)
app.debug = True

db = shelve.open("shorten.db")


###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
#@app.route('/home', methods=['GET'])
#def home():
#    """Builds a template based on a GET request, with some default
#    arguements"""
#    index_title = request.args.get("title", "i253")
#    hello_name = request.args.get("name", "Jim")
#    return flask.render_template(
#            'home.html',
#            title=index_title,
#            name=hello_name)

###
# Wiki Resource:
# GET method will redirect to the resource stored by PUT, by default: Wikipedia.org
# POST/PUT method will update the redirect destination
###

#@app.route('/wiki', methods=['GET'])
#def wiki_get():
#    """Redirects to wikipedia."""
#    destination = db.get('wiki', 'http://en.wikipedia.org')
#    app.logger.debug("Redirecting to " + destination)
#    return flask.redirect(destination)

#@app.route("/wiki", methods=['PUT', 'POST'])
#def wiki_put():
#    """Set or update the URL to which this resource redirects to. Uses the
#    `url` key to set the redirect destination."""
#    wikipedia = request.form.get('url', 'http://en.wikipedia.org')
#    db['wiki'] = wikipedia
#    return "Stored wiki => " + wikipedia


@app.route("/shorts", methods=['PUT', 'POST'])
def shorts_post():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    url = request.form.get('url', 'http://www.google.com')
    alias1 = request.form.get('alias', 'google')
    alias = alias1.encode('ascii','ignore')
    db[alias] = url
    return flask.render_template(
        'home.html',
        alias=alias)

#    return flask.render_template(
#            'shorts.html',
#            alias=alias,
#            url=url)

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


###
# i253 Resource:
# Information on the i253 class. Can be parameterized with `relationship`,
# `name`, and `adjective` information
#
# TODO: The representation for this resource is broken. Fix it!
# Set the correct MIME type to be able to view the image in your browser
##/
#@app.route('/i253')
#def i253():
#    """Returns a PNG image of madlibs text"""
#    relationship = request.args.get("relationship", "friend")
#    name = request.args.get("name", "Jim")
#    adjective = request.args.get("adjective", "fun")

#    resp = flask.make_response(
 
#           check_output(['convert', '-size', '600x400', 'xc:transparent',
#                '-frame', '10x30',
#                '-font', '/usr/share/fonts/liberation/LiberationSerif-BoldItalic.ttf',
#                '-fill', 'black',
#                '-pointsize', '32',
#                '-draw',
#                  "text 30,60 'My %s %s said i253 was %s'" % (relationship, name, adjective),
#                '-raise', '30',
#                'png:-']), 200);
    # Comment in to set header below
    # resp.headers['Content-Type'] = '...'

#    return resp


if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))
