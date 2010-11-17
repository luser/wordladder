#!/usr/bin/env python

import web
import os
import hmac
import hashlib
from time import *

from json import dump_json, load_json
from google.appengine.ext import db
from config import HASHKEY

class User(db.Model):
	username = db.StringProperty(required=False)
	created = db.DateTimeProperty(required=True, auto_now_add=True)

	def __str__(self):
		if self.username:
			return "%s" % (self.username)
		else:
			return "Unknown"

	def _obj(self):
		return {'key': self.key().name(),
						'username': self.username,
            'created': mktime(self.created)}

	def isAnonymous(self):
		if self.services.count(1) == 0:
			return True
		return False

	def json(self):
		return dump_json(self._obj())

	@staticmethod
	def fromJSON(json):
		j = load_json(json)
		return User(key_name=j['key'], username=j['username'], created=j['created'])

	@staticmethod
	def currentUser():
		cookies = web.cookies()
		if ("wl_identity" in cookies):
			identity = cookies["wl_identity"]
			if identity:
				parts = identity.split("/")
			else:
				return makeAnonUser()
			if (hmac.new(HASHKEY, parts[0], hashlib.sha1).hexdigest() == parts[1]):
				user = User.get_by_key_name(key_names=parts[0])
				if user:
					return user
				else:
					return makeAnonUser()
			else:
				raise web.badrequest()
		else:
			return makeAnonUser()

	def setUsername(username):
		self.username = username
		self.put()
		return True

class UserService(db.Model):
	name = db.StringProperty(required=True)
	user = db.ReferenceProperty(User, collection_name="services")
	user_service_id = db.StringProperty(required=True)
	access_token = db.StringProperty(required=True)
	url = db.LinkProperty(required=False)
	created = db.DateTimeProperty(required=True, auto_now_add=True)

	def __str__(self):
		if self.url:
			return "%s" % self.url
		else:
			return "%s on %s" % self.user_service_id, self.name

	def _obj(self):
		return {'key': self.key().name(),
						'name': self.name,
						'user': self.user.key(),
						'user_service_id': self.user_service_id,
						'access_token': self.access_token,
						'url': self.url,
						'created': self.created}

	def json(self):
		return dump_json(self._obj())

	@staticmethod
	def fromJSON(json):
		j = load_json(json)
		return UserService(key_name=j['key'], name=j['name'], user=j['user'], user_service_id=j['user_service_id'], access_token=j['access_token'], url=j['url'], created=j['created'])

def makeAnonUser():
	user = User(key_name='anon-' + hmac.new(HASHKEY, str(web.ctx.ip) + str(web.ctx.env['HTTP_USER_AGENT'])).hexdigest())
	user.put()
	if user:
		web.setcookie('wl_identity', user.key().name() + '/' + hmac.new(HASHKEY, user.key().name(), hashlib.sha1).hexdigest(), expires=mktime(localtime()) + 30 * 86400)
		return user
	else:
		return None
