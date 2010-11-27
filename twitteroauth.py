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

TWITTER_APP_ID = 'KA7MDZJX1mHGiqMW1B4w'
TWITTER_APP_SECRET = '8bihxc4NCRQtTlz3BFJnuJCn38AjnDtXh6jSbHlMPPU'

TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

import hashlib, hmac
import os.path, random
import web, cgi, urllib, urllib2

from json import dump_json, load_json
from google.appengine.ext import db
from data import web_host
from user import *
from time import *
from session import *
import config
from base64 import encodestring as base64encode

class twitterOAuth():
	@staticmethod
	def defaultArgs():
		return dict(oauth_consumer_key = config.TWITTER_APP_ID_LOCAL if hasattr(config, 'TWITTER_APP_ID_LOCAL') else TWITTER_APP_ID,
								oauth_nonce = ''.join([str(random.randint(0, 9)) for i in range(8)]),
								oauth_signature_method = 'HMAC-SHA1',
								oauth_timestamp = int(mktime(localtime())))

	@staticmethod
	def authorize(params):
		oauth_token = (params['oauth_token'] if params['oauth_token'] else None)
		oauth_verifier = (params['oauth_verifier'] if params['oauth_verifier'] else None)
		args = twitterOAuth.defaultArgs()

		if oauth_token and oauth_verifier:
			args.update({'oauth_token': oauth_token, 'oauth_verifier': oauth_verifier})
			args['oauth_signature'] = twitterOAuth.sign(TWITTER_ACCESS_TOKEN_URL, args)
			try:
				response = urllib2.urlopen(TWITTER_ACCESS_TOKEN_URL + '?' + urllib.urlencode(args)).read()
			except:
				User.currentSession().addMessage('error', "Couldn't get access token from Twitter. Please try again in a few minutes.")
				return web.seeother('/')

			response = cgi.parse_qs(response)

			if 'oauth_token' not in response or 'oauth_token_secret' not in response:
				User.currentSession().addMessage('error', "Didn't get the expected response from Twitter.")
				return web.seeother('/')

			oauth_token = response['oauth_token'][-1]
			oauth_token_secret = response['oauth_token_secret'][-1]

			service = twitterOAuth.updateProfile(oauth_token, oauth_token_secret)

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
			return web.seeother('/')			
		else:
			User.currentSession().deleteKey('token_secret')
			args.update(oauth_callback=web_host() + '/user/login/twitter')
			args['oauth_signature'] = twitterOAuth.sign(TWITTER_REQUEST_TOKEN_URL, args)

			try:
				response = urllib2.urlopen(TWITTER_REQUEST_TOKEN_URL + '?' + urllib.urlencode(args)).read()
			except:
				User.currentSession().addMessage('error', "Couldn't request OAuth token from Twitter. Please try again in a few minutes.")
				return web.seeother('/')

			response = cgi.parse_qs(response)

			if 'oauth_token' in response and 'oauth_token_secret' in response:
				oauth_token = response['oauth_token'][-1]
				oauth_token_secret = response['oauth_token_secret'][-1]
				User.currentSession().setKey('token_secret', oauth_token_secret)
				return web.seeother(TWITTER_AUTHORIZE_URL + '?oauth_token=' + urllib.quote(oauth_token));
			else:
				User.currentSession().addMessage('error', "Twitter's response didn't contain the information we expected. Please try again in a few minutes.")
				return web.seeother('/')

	@staticmethod
	def sign(url, request):
		key = urllib.quote(config.TWITTER_APP_SECRET_LOCAL if hasattr(config, 'TWITTER_APP_SECRET_LOCAL') else TWITTER_APP_SECRET, '') + '&'
		secret = User.currentSession().get_and_delete('token_secret')
		if secret:
			key += urllib.quote(secret, '')
		base_string = 'GET&' + urllib.quote(url, '') + '&'
		base_string += urllib.quote('&'.join('%s=%s' % (urllib.quote(str(k), ''), urllib.quote(str(request[k]), '')) for k in sorted(request.iterkeys())), '')
		return base64encode(hmac.new(key, base_string, hashlib.sha1).digest())[:-1]

	@staticmethod
	def updateProfile(access_token, access_token_secret):
		args = twitterOAuth.defaultArgs()
		url = 'http://api.twitter.com/1/account/verify_credentials.json'
		args.update(oauth_token=access_token)
		User.currentSession().setKey('token_secret', access_token_secret)
		args['oauth_signature'] = twitterOAuth.sign(url, args)
		
		try:
			profile = load_json(urllib2.urlopen(url + '?' + urllib.urlencode(args)).read())
		except:
			User.currentSession().addMessage('error', "Couldn't access your Twitter profile.")
			profile = False

		if profile:
			service = UserService.get_or_insert(key_name='twitter-' + str(profile['id']), access_token=str(access_token), access_token_secret=str(access_token_secret), name='twitter', username=str(profile['name']), user_service_id=str(profile['id']), picture=str(profile['profile_image_url']), url=str('http://twitter.com/' + profile['screen_name']))
			service.access_token = str(access_token)
			service.access_token_secret = str(access_token_secret)
			service.name='twitter'
			service.username = str(profile['name'])
			service.user_service_id = str(profile['id'])
			service.picture = str(profile['profile_image_url'])
			service.url = str('http://twitter.com/'+profile['screen_name'])
			
			user = User.currentUser()
			if service.user and service.user.key().name() != user.key().name():
				service.user.mergeWith(user)
				user = service.user
				user.put()
			else:
				service.user = user

			service.put()
			return service
		else:
			return False
