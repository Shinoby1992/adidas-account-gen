import requests
from bs4 import BeautifulSoup as bs
from random import *
from time import sleep
import string
import _thread
import json
from flask import Flask, render_template, request, redirect
from datetime import datetime
import logging
import webbrowser
import sys

from utils import Logger


tokens = []

def captureToken(token):
	expiry = datetime.now().timestamp() + 115
	tokenDict = {
		'expiry': expiry,
		'token': token
	}
	tokens.append(tokenDict)
	return

def sendToken():
	while not tokens:
		pass
	token = tokens.pop(0)
	return token['token']

def manageTokens():
	while True:
		for item in tokens:
			if item['expiry'] < datetime.now().timestamp():
				tokens.remove(item)
		sleep(5)

# app = Flask(__name__, template_folder='C:\AccountGenerator\\templates', static_folder='C:\AccountGenerator\static')
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/', methods=['GET'])
def base():
	return redirect("http://fuckrsvpkingz.adidas.co.uk:5000/solve", code=302)

@app.route('/solve', methods=['GET'])
def solve():
	sitekey = "6LdyFRkUAAAAAF2YmQ9baZ6ytpVnbVSAymVpTXKi"
	return render_template('index.html', sitekey=sitekey)


@app.route('/submit', methods=['POST'])
def submit():
	token = request.form['g-recaptcha-response']
	captureToken(token)
	return redirect("http://fuckrsvpkingz.adidas.co.uk:5000/solve", code=302)


class Generator():

	def __init__(self, locale, sitekey, pageurl):
		self.locale = locale.upper()
		if locale.upper() == "UK":
			self.domain = '.co.uk'
			self.language = 'en_GB'
		else:
			self.domain = '.com'
			self.language = 'en_US'
		self.sitekey = sitekey

	def create_account(self, email, password, captcha_token):		
		headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
			'Accept-Encoding': 'gzip, deflate, sdch, br',
			'Accept-Language': 'en-GB,en;q=0.8',
			'Upgrade-Insecure-Requests': '1'
		}
		s = requests.Session()
		s.headers.update(headers)
		r = s.get('https://cp.adidas{}/web/eCom/{}/loadcreateaccount'.format(self.domain, self.language))
		csrftoken = bs(r.text, "html.parser").find('input', {'name': 'CSRFToken'})['value']
		s.headers.update({
			'Origin': 'https://cp.adidas{}'.format(self.domain),
			'Referer': 'https://cp.adidas{}/web/eCom/{}/loadcreateaccount'.format(self.domain, self.language)
			})
		data = {
			'firstName': 'John',
			'lastName': 'Smith',
			'minAgeCheck': 'true',
			'day': '23',
			'month': '05',
			'year': '1998',
			'_minAgeCheck': 'on',
			'email': email,
			'password': password,
			'confirmPassword': password,
			'_amf': 'on',
			'terms': 'true',
			'_terms': 'on',
			'metaAttrs[pageLoadedEarlier]': 'true',
			'app': 'eCom',
			'locale': self.language,
			'domain': '',
			'consentData1': 'Sign me up for adidas emails, featuring exclGBive offers, featuring latest product info, news about upcoming events, and more. See our <a target="_blank" href="https://www.adidas.co.uk/GB/help-topics-privacy_policy.html">Policy Policy</a> for details.',
			'consentData2': '',
			'consentData3': '',
			'CSRFToken': csrftoken,
			'g-recaptcha-response': captcha_token
			}
		r = s.post('https://cp.adidas{}/web/eCom/{}/accountcreate'.format(self.domain, self.language), data=data)
		account = '{}:{}'.format(email, password)
		if r.status_code == requests.codes.ok:
			return True, account
		else:
			return False, None



if __name__ == '__main__':
	logger = Logger()
	logger.log("Adidas Account Creator v1.1.0")
	logger.log("@ryan9918_")
	logger.log("***************************************************************************")
	with open('config.json') as file:
		config = json.load(file)
		file.close()
	try:
		with open('C:\Windows\System32\drivers\etc\hosts') as file:
			if "127.0.0.1 fuckrsvpkingz.adidas.co.uk" not in file.read():
				with open('C:\Windows\System32\drivers\etc\hosts', 'a') as file:
					file.write("\n\n# Adidas Account Generator")
					file.write("\n127.0.0.1 fuckrsvpkingz.adidas.co.uk")
					file.close()
			else:
				file.close()
	except PermissionError:
		logger.error("Failed to edit hosts file. Make sure to run as admin or edit hosts file manually.")
		input("")
		sys.exit()
	except:
		logger.error("Failed to edit hosts file. Make sure to edit the hosts file manually before continuing if this has not been done already.")
	_thread.start_new_thread(app.run, ())
	_thread.start_new_thread(manageTokens, ())
	accountsList = []
	creator = Generator(config['locale'], '6LdyFRkUAAAAAF2YmQ9baZ6ytpVnbVSAymVpTXKi', 'https://www.adidas.com')
	num = input("# ACCOUNTS: ")
	webbrowser.open('http://fuckrsvpkingz.adidas.co.uk:5000/solve')
	logger.status("Started account generator.")
	for x in range(int(num)):
		email = '{}-{}@{}'.format(config['prefix'], randint(1111,999999999), config['domain'])
		allchar = string.ascii_letters + string.digits
		passw = "".join(choice(allchar) for x in range(randint(8, 12)))
		logger.warn("Task {} - Waiting for captcha token.".format(x))
		token = sendToken()
		logger.log("Task {} - Obtained captcha token.".format(x))
		result, account = creator.create_account(email, passw, token)
		if result:
			logger.success("Task {} - Created account {}".format(x, account))
			accountsList.append(account)
		else:
			logger.error("Task {} - Failed to create account.".format(x))
	with open('accounts.txt', 'w') as file:
		for item in accountsList:
			file.write('{}\n'.format(item))
		file.close()
	logger.status("Saved accounts to txt file.")
