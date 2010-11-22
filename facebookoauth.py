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

import hashlib
import hmac
import os.path
import urllib
import web
import cgi

from urllib2 import urlopen as urlopen
from json import dump_json, load_json
from google.appengine.ext import db
from data import web_host
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
			response = cgi.parse_qs(urlopen(FACEBOOK_ACCESS_TOKEN_URL + '?' + urllib.urlencode(args)).read())
			token = response['access_token'][-1]
			profile = load_json(urlopen('https://graph.facebook.com/me?fields=id,name,link,picture&' + urllib.urlencode(dict(access_token = token))).read())

			service = UserService.get_or_insert(key_name='facebook-' + str(profile['id']), access_token=str(token), name='facebook', user_service_id=str(profile['id']), url=str(profile['link']), picture=str(profile['picture']))

			if service.user:
				service.user.mergeWith(User.currentUser())
				user = service.user
			else:
				user = User.currentUser()

			if not user.username:
				user.username = str(profile['name'])
			if not user.picture:
				user.picture = str(profile['picture'])
			user.put()

			service.user = user
			service.put()

			user.login()
			web.seeother('/')			
		else:
			web.seeother(FACEBOOK_AUTHORIZE_URL + '?' + urllib.urlencode(args))
