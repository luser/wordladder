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

GOOGLE_APP_ID = 'anonymous'
GOOGLE_APP_SECRET = 'anonymous'

GOOGLE_REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
GOOGLE_AUTHORIZE_URL = 'https://www.google.com/accounts/OAuthAuthorizeToken'
GOOGLE_ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'

import hashlib
import hmac
import os.path
import urllib
import web
import cgi
import random

from urllib2 import urlopen as urlopen
from json import dump_json, load_json
from google.appengine.ext import db
from data import web_host
from user import *
from time import *
from session import *
from config import HASHKEY
from base64 import encodestring as base64encode

class googleOAuth():
	@staticmethod
	def authorize(params):
		oauth_token = (params['oauth_token'] if params['oauth_token'] else None)
		oauth_verifier = (params['oauth_verifier'] if params['oauth_verifier'] else None)

		args = dict(oauth_consumer_key = GOOGLE_APP_ID,
								oauth_nonce = ''.join([str(random.randint(0, 9)) for i in range(8)]),
								oauth_signature_method = 'HMAC-SHA1',
								oauth_timestamp = int(mktime(localtime())))

		if oauth_token and oauth_verifier:
			args.update({'oauth_token': oauth_token, 'oauth_verifier': oauth_verifier})
			args['oauth_signature'] = googleOAuth.sign(GOOGLE_ACCESS_TOKEN_URL, args)
			response = cgi.parse_qs(urlopen(GOOGLE_ACCESS_TOKEN_URL + '?' + urllib.urlencode(args)).read())
			oauth_token = response['oauth_token'][-1]
			oauth_token_secret = response['oauth_token_secret'][-1]
			User.currentSession().setKey('token_secret', oauth_token_secret)

			# recalculate sig for next request
			url = 'https://www.googleapis.com/buzz/v1/people/@me/@self'
			args.update(oauth_token=oauth_token, alt='json')
			del args['oauth_signature']
			del args['oauth_verifier']
			args['oauth_signature'] = googleOAuth.sign(url, args)
			profile = load_json(urlopen(url + '?' + urllib.urlencode(args)).read())
			service = UserService.get_or_insert(key_name='googlebuzz-' + str(profile['data']['id']), access_token=str(oauth_token), access_token_secret=str(oauth_token_secret), name='googlebuzz', user_service_id=str(profile['data']['id']), picture=str(profile['data']['thumbnailUrl']), url=str(profile['data']['profileUrl']))

			if service.user:
				service.user.mergeWith(User.currentUser())
				user = service.user
			else:
				user = User.currentUser()

			if not user.username:
				user.username = str(profile['data']['displayName'])
			if not user.picture:
				user.picture = str(profile['data']['thumbnailUrl'])
			user.put()

			service.user = user
			service.put()

			user.login()
			return web.seeother('/')			
		else:
			User.currentSession().deleteKey('token_secret')
			args.update(oauth_callback=web_host() + '/user/login/google', scope='https://www.googleapis.com/auth/buzz')
			args['oauth_signature'] = googleOAuth.sign(GOOGLE_REQUEST_TOKEN_URL, args)
			response = cgi.parse_qs(urlopen(GOOGLE_REQUEST_TOKEN_URL + '?' + urllib.urlencode(args)).read())
			oauth_token = response['oauth_token'][-1]
			oauth_token_secret = response['oauth_token_secret'][-1]
			User.currentSession().setKey('token_secret', oauth_token_secret)
			return web.seeother(GOOGLE_AUTHORIZE_URL + '?oauth_token=' + urllib.quote(oauth_token));

	@staticmethod
	def sign(url, request):
		key = urllib.quote(GOOGLE_APP_SECRET, '') + '&'
		secret = User.currentSession().get_and_delete('token_secret')
		if secret:
			key += urllib.quote(secret, '')
		base_string = 'GET&' + urllib.quote(url, '') + '&'
		base_string += urllib.quote('&'.join('%s=%s' % (urllib.quote(str(k), ''), urllib.quote(str(request[k]), '')) for k in sorted(request.iterkeys())), '')
		return base64encode(hmac.new(key, base_string, hashlib.sha1).digest())[:-1]
