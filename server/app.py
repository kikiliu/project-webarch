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

    user_id = request.cookies.get('user_id').encode('ascii', 'ignore')
    if user_id is None:
        user_id = generate_user_id(11111)
        expiresTime = datetime.datetime.now() + datetime.timedelta(days = 365)
        resp.set_cookie('user_id', user_id, expires=expiresTime, path='/')
    return resp


@app.route("/shorts", methods=['PUT', 'POST'])
def shorts_post():
	"""Set or update the URL to which this resource redirects to. Uses the
	`url` key to set the redirect destination."""
	url = request.form.get('url').encode('ascii', 'ignore')
	user_set_alias = user_set_alias = request.form.get('alias').encode('ascii', 'ignore')
    
	alias = db_url.get(url)
	if alias is None:
		if user_set_alias == '':
			alias = random_alias()
		else:
			alias = user_set_alias                                                       # if url in not in current db, try to get user-specified alias or random alia
												              # if user sets alias AND the alias is not in current db, assgin the ali

	db_url[url] = alias
	db_alias[alias] = url

#Added by Rahul----------------------------------------------------------------------------------------------
	cookie_id = str(request.cookies.get('user_id'))
	soup = BeautifulSoup(urllib2.urlopen(url))
	title = str(soup.title.string)
	comments = str(request.form.get('comment'))
	date = time.strftime("%d/%m/%Y %H:%M:%S")
	tuple_new = (title,url,date,comments)
	list_hist = db_history.get(cookie_id)
	if list_hist == None:
		db_history[cookie_id] = list(tuple_new)
	else:
		list_hist.append(tuple_new)
		db_history[cookie_id] = list_hist
	app.logger.debug(db_history.get(cookie_id))
#modification ends here---------------------------------------------------------------------------------------
 
    	app.logger.debug('alias = ' + alias + ' url = ' + url)
	return flask.render_template('Test.html',alias=alias,display_style='',display_history='')

#Added by Rahul----------------------------------------------------------------------------------------------
@app.route("/history", methods=['PUT', 'POST'])
def history_get():
    	"""Gets the userid from the cookie and the word from the
    	text box and searches the user db for the matching comments. Once it has all
    	the details, it will create a li with title, alias, date, and comments and
    	return as text"""
    	cookie_userid = str(request.cookies.get('user_id'))
    	search_word = str(request.form.get('search_term'))
    	history_tuple = db_history.get(cookie_userid)
    	data = ''
    	regex = re.compile("|".join(search_word.lower().split()))
    	history_list = db_history.get(cookie_userid)
	if history_list != None:
		for index,value in enumerate(history_list):
        		if regex.search(value[3].lower()):
            			data += "<li><span class=history_section>" + value[0] + ", <a href=" + value[1] + ">" + value[1] + "</a>, " + value[2] + "<span class=comment_section>" + value[3] + "</span></span></li>"	
    	if data == '':
		data = '<li><span class=history_section>No match found</span></li>'
    	return jsonify(result=data)
#modification ends here---------------------------------------------------------------------------------------


if __name__ == "__main__":
	app.debug = True
    	app.run(port=int(environ['FLASK_PORT']))
