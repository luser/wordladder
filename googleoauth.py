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

import hmac, hashlib
import os.path, random
import web, cgi, urllib

from urllib2 import urlopen as urlopen, URLError, HTTPError
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
	def defaultArgs():
		return dict(oauth_consumer_key = GOOGLE_APP_ID,
								oauth_nonce = ''.join([str(random.randint(0, 9)) for i in range(8)]),
								oauth_signature_method = 'HMAC-SHA1',
								oauth_timestamp = int(mktime(localtime())))

	@staticmethod
	def authorize(params):
		oauth_token = (params['oauth_token'] if params['oauth_token'] else None)
		oauth_verifier = (params['oauth_verifier'] if params['oauth_verifier'] else None)
		args = googleOAuth.defaultArgs()

		if oauth_token and oauth_verifier:
			args.update({'oauth_token': oauth_token, 'oauth_verifier': oauth_verifier})
			args['oauth_signature'] = googleOAuth.sign(GOOGLE_ACCESS_TOKEN_URL, args)
			try:
				response = urlopen(GOOGLE_ACCESS_TOKEN_URL + '?' + urllib.urlencode(args)).read()
			except:
				User.currentSession().addMessage('error', "Couldn't fetch OAuth access token from Google. Please try again in a few minutes.")
				return web.seeother('/')

			response = cgi.parse_qs(response)
			if 'oauth_token' not in response or 'oauth_token_secret' not in response:
				User.currentSession().addMessage('error', "Google's response didn't contain the information we expected. Please try again in a few minutes.")
				return web.seeother('/')

			oauth_token = response['oauth_token'][-1]
			oauth_token_secret = response['oauth_token_secret'][-1]

			service = googleOAuth.updateProfile(oauth_token, oauth_token_secret)
			if not service:
				User.currentSession().addMessage('error', 'Could not update Google profile.')
				return web.seeother('/')

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
			User.currentSession().addMessage('info', "Successfully logged into your Google account.")
			return web.seeother('/')
		else:
			User.currentSession().deleteKey('token_secret')
			args.update(oauth_callback=web_host() + '/user/login/google', scope='https://www.googleapis.com/auth/buzz https://www.google.com/m8/feeds/')
			args['oauth_signature'] = googleOAuth.sign(GOOGLE_REQUEST_TOKEN_URL, args)
			try:
				response = urlopen(GOOGLE_REQUEST_TOKEN_URL + '?' + urllib.urlencode(args)).read()
			except:
				User.currentSession().addMessage('error', "Couldn't request OAuth token from Google. Please try again in a few minutes.")
				return web.seeother('/')

			response = cgi.parse_qs(response)
			if 'oauth_token' in response and 'oauth_token_secret' in response:
				oauth_token = response['oauth_token'][-1]
				oauth_token_secret = response['oauth_token_secret'][-1]
				User.currentSession().setKey('token_secret', oauth_token_secret)
				return web.seeother(GOOGLE_AUTHORIZE_URL + '?oauth_token=' + urllib.quote(oauth_token));
			else:
				User.currentSession().addMessage('error', "Google's response didn't contain the information we expected. Please try again in a few minutes.")
				return web.seeother('/?f=0.5')

	@staticmethod
	def sign(url, request):
		key = urllib.quote(GOOGLE_APP_SECRET, '') + '&'
		secret = User.currentSession().get_and_delete('token_secret')
		if secret:
			key += urllib.quote(secret, '')
		base_string = 'GET&' + urllib.quote(url, '') + '&'
		base_string += urllib.quote('&'.join('%s=%s' % (urllib.quote(str(k), ''), urllib.quote(str(request[k]), '')) for k in sorted(request.iterkeys())), '')
		return base64encode(hmac.new(key, base_string, hashlib.sha1).digest())[:-1]

	@staticmethod
	def updateProfile(access_token, access_token_secret):
		# First try getting Buzz profile, mostly for the picture.
		args = googleOAuth.defaultArgs()
		url = 'https://www.googleapis.com/buzz/v1/people/@me/@self'
		args.update(oauth_token=access_token, alt='json')
		User.currentSession().setKey('token_secret', access_token_secret)
		args['oauth_signature'] = googleOAuth.sign(url, args)
		try:
			bprofile = load_json(urlopen(url + '?' + urllib.urlencode(args)).read())
		except (URLError, HTTPError):
			User.currentSession().addMessage('warning', "Couldn't access your Google Buzz profile (maybe you don't have one?).")
			bprofile = False

		# Then get the Contacts profile.
		args = googleOAuth.defaultArgs()
		url = 'https://www.google.com/m8/feeds/contacts/default/full'
		args.update(oauth_token=access_token, alt='json')
		User.currentSession().setKey('token_secret', access_token_secret)
		args['oauth_signature'] = googleOAuth.sign(url, args)
		try:
			cprofile = load_json(urlopen(url + '?' + urllib.urlencode(args)).read())
		except (URLError, HTTPError):
			User.currentSession().addMessage('error', "Couldn't access your Google Contacts profile. This is required for authenticating with your Google account.")
			cprofile = False

		# Contacts profile is required.
		if cprofile:
			service = UserService.get_or_insert(key_name='google-' + str(cprofile['feed']['id']['$t']), access_token=str(access_token), access_token_secret=str(access_token_secret), name='google', user_service_id=str(cprofile['feed']['id']['$t']))
			service.access_token = str(access_token)
			service.access_token_secret = str(access_token_secret)
			service.name='google'
			service.username = str(cprofile['feed']['author'][0]['name']['$t'])
			service.user_service_id = str(cprofile['feed']['id']['$t'])
			service.email = str(cprofile['feed']['author'][0]['email']['$t'])

			if bprofile:
				if len(str(bprofile['data']['displayName'])) > len(str(service.username)):
					service.username = str(bprofile['data']['displayName'])
				service.picture = str(bprofile['data']['thumbnailUrl'])
				service.url = str(bprofile['data']['profileUrl'])
			
			if not service.picture and service.email:
				gravatar_url = "http://www.gravatar.com/avatar.php?"
				gravatar_url += urllib.urlencode({'gravatar_id': hashlib.md5(service.email.lower()).hexdigest(), 'size': '50', 'default': 'identicon'})
				service.picture = gravatar_url

			user = User.currentUser()
			if service.user and service.user.key().name() != user.key().name():
				service.user.mergeWith(user)
				service.user.put()
			else:
				service.user = user

			service.put()
			return service
		else:
			return False
