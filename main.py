import requests
from bs4 import BeautifulSoup as bs
from random import randint, choice
from time import sleep
import string
import _thread
import json
from flask import Flask, render_template, request, redirect
from datetime import datetime
import logging
import webbrowser
import sys
from faker import Faker

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
	sitekey = "6LdC0iQUAAAAAOYmRv34KSLDe-7DmQrUSYJH8eB_"
	return render_template('index.html', sitekey=sitekey)


@app.route('/submit', methods=['POST'])
def submit():
	token = request.form['g-recaptcha-response']
	captureToken(token)
	return redirect("http://fuckrsvpkingz.adidas.co.uk:5000/solve", code=302)


class Generator():

	def __init__(self, sitekey, pageurl):
		self.sitekey = sitekey
		self.faker = Faker()
		self.headers = {
			'Origin': 'https://cp.adidas.co.uk',
			'Referer': 'https://cp.adidas.co.uk/web/eCom/en_GB/loadcreateaccount',
			'x-client-id': '62wi38jgwliizcyxz5f193dtfoweqywh'
			}

	def create_account(self, email, password, captcha_token):
		name = self.faker.name()
		payload = {
			'source': '40',
			'account': {
				'firstName': name[0],
				'lastName': name[1],
				'email': email,
				'password': password,
				'confirmPassword': password,
				'dateOfBirth': '{}-{}-{}'.format(randint(1970,1995), randint(1,11), randint(1,25))
			},
			'communicationLanguage': 'en',
			'countryOfSite': 'GB',
			'detectionCookie': 'eCom|en_GB|cp.adidas.co.uk|null',
			'idpAdapterId': 'adidasIdP10',
			'inErrorResource': 'https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/null',
			'loginUrl': 'https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/MyAccount-CreateOrLogin',
			'partnerSpId': 'sp:demandware',
			'pfStartSSOURL': 'https://cp.adidas.co.uk/idp/startSSO.ping',
			'profile': {
				'consumerAttributes': []
			},
			'reCaptchaResponse': captcha_token,
			'subscription': {
				'serviceId': ['100'],
				'consents': [{
					'consentType': 'AMF',
					'consentValue': False
				}]
			},
			'targetResource': 'https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/MyAccount-ResumeRegister?target=account'
		}
		r = requests.post('https://crm.adidas.com/accounts/createAccount', json=payload, headers=self.headers)
		account = '{}:{}'.format(email, password)
		if r.json()['title'] == "Registration successful":
			return True, account
		else:
			return False, None



if __name__ == '__main__':
	logger = Logger()
	logger.log("Adidas Account Creator v2.0")
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
	creator = Generator('6LdC0iQUAAAAAOYmRv34KSLDe-7DmQrUSYJH8eB_', 'https://www.adidas.com')
	num = input("# ACCOUNTS: ")
	webbrowser.open('http://fuckrsvpkingz.adidas.co.uk:5000/solve')
	logger.status("Started account generator.")
	for x in range(int(num)):
		email = '{}-{}@{}'.format(config['prefix'], randint(1111,999999999), config['domain'])
		if config['useRandomPassword']:
			allchar = string.ascii_letters + string.digits
			passw = "".join(choice(allchar) for x in range(randint(8, 12)))
		else:
			passw = config['fixedPassword']
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
