# Based on https://github.com/facebook/python-sdk/blob/master/examples/oauth/facebookoauth.py
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

FACEBOOK_APP_ID = '2ee02710218dfab2787add30e13408ba'
FACEBOOK_APP_SECRET = 'a2f057029372cbb02e31094c23dfd40f'

FACEBOOK_AUTHORIZE_URL = 'https://graph.facebook.com/oauth/authorize'
FACEBOOK_ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'

import hashlib, hmac
import os.path
import web, cgi, urllib

from urllib2 import urlopen as urlopen
from json import dump_json, load_json
from google.appengine.ext import db
from app import *
from user import *
from time import *
from config import HASHKEY

class facebookOAuth():
	@staticmethod
	def authorize(params):
		code = (params['code'] if params['code'] else None)

		args = dict(client_id = FACEBOOK_APP_ID, redirect_uri = web_host() + '/user/login/facebook')
		if code:
			args.update(client_secret=FACEBOOK_APP_SECRET, code=code)
			try:
				response = urlopen(FACEBOOK_ACCESS_TOKEN_URL + '?' + urllib.urlencode(args)).read()
			except:
				User.currentSession().addMessage('error', "Couldn't get access token from Facebook. Please try again in a few minutes.")
				web.seeother('/')

			response = cgi.parse_qs(response)
			if not 'access_token' in response:
				User.currentSession().addMessage('error', "The response from Facebook didn't contain the information we expected. Please try again in a few minutes.")
				web.seeother('/')

			token = response['access_token'][-1]
			service = facebookOAuth.updateProfile(token, False)

			if service.user:
				user = service.user
			else:
				user = User.currentUser()

			if not user.username:
				user.username = service.username
			if not user.picture:
				user.picture = service.picture
			user.put()

			user.login()
			User.currentSession().addMessage('info', "Successfully logged you into your Facebook account.")
			web.seeother('/')			
		else:
			web.seeother(FACEBOOK_AUTHORIZE_URL + '?' + urllib.urlencode(args))

	@staticmethod
	def updateProfile(access_token, access_token_secret = False):
		try:
			response = urlopen('https://graph.facebook.com/me?fields=id,name,link,picture&' + urllib.urlencode(dict(access_token = access_token))).read()
		except:
			User.currentSession().addMessage('error', "Couldn't get profile information from Facebook. Please try again in a few minutes.")
			return False

		profile = load_json(response)
		if profile:
			service = UserService.get_or_insert(key_name='facebook-' + str(profile['id']), access_token=str(access_token), name='facebook', user_service_id=str(profile['id']), url=str(profile['link']), picture=str(profile['picture']))
			service.access_token = str(access_token)
			service.name = 'facebook'
			service.username = str(profile['name'])
			service.user_service_id = str(profile['id'])
			service.url = str(profile['link'])
			service.picture = str(profile['picture'])
			
			if service.user:
				service.user.mergeWith(User.currentUser())
				service.user.put()
			else:
				service.user = User.currentUser()
	
			service.put()
			return service
		else:
			return False

