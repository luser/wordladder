#!/usr/bin/env python

import web
import os
import hmac
import hashlib
from time import *
from session import *

from json import dump_json, load_json
from google.appengine.ext import db
from config import HASHKEY

class User(db.Model):
	username = db.StringProperty(required=False)
	picture = db.LinkProperty(required=False)
	score = db.IntegerProperty(required=False, default=0)
	created = db.DateTimeProperty(required=True, auto_now_add=True)

	def __str__(self):
		if self.username:
			return "%s" % (self.username)
		else:
			return "Unknown"

	def _obj(self):
		return {'key': self.key().name(),
						'username': self.username,
						'picture': self.picture,
						'score': self.score,
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
		return User(key_name=j['key'], username=j['username'], picture=j['picture'], score=j['score'], created=j['created'])

	@staticmethod
	def currentUser():
		cookies = web.cookies()
		if ("wl_identity" in cookies):
			identity = cookies["wl_identity"]
			if identity:
				parts = identity.split("/")
				if (hmac.new(HASHKEY, parts[0], hashlib.sha1).hexdigest() == parts[1]):
					user = User.get_by_key_name(key_names=parts[0])
					if user:
						return user
		return User.makeAnonUser()

	@staticmethod
	def currentSession():
		u = User.currentUser()
		session = u.session.get()
		if not session:
			session = Session(key_name='session-' + u.key().name(), user=u)
			session.put()
		return session				

	def setUsername(self, username):
		self.username = username
		self.put()
		return True

	@staticmethod
	def makeAnonUser():
		user = User(key_name='user-' + hmac.new(HASHKEY, str(mktime(localtime())) + str(web.ctx.ip) + str(web.ctx.env['HTTP_USER_AGENT'])).hexdigest())
		user.put()
		if user.put():
			user.login()
			return user
		else:
			return None

	def mergeWith(self, u):
		# Take u's info and roll it into self, then eliminate u
		if u.username and not self.username:
			self.username = u.username

		if u.picture and not self.picture:
			self.picture = u.picture

		if u.score:
			self.score += u.score
		
		# TODO: Should we allow multiple accounts on the same service?
		for uS in u.services:
			if uS.name not in [mS.name for mS in self.services]:
				uS.user = self
				uS.put()
			else:
				uS.delete()

		uSession = u.session.get()
		if uSession:
			mySession = self.currentSession()
			for uP in uSession.params:
				if uP.name not in [mP.name for mP in mySession.params]:
					uP.session = mySession
					uP.put()
				else:
					# TODO: Handle specific session params that should get merged in some other way.
					uP.delete()
			uSession.delete()

		for uM in u.moves:
			uM.user = self
			uM.put()

		u.delete()
		return self.login()

	def login(self):
		return web.setcookie('wl_identity', self.key().name() + '/' + hmac.new(HASHKEY, self.key().name(), hashlib.sha1).hexdigest(), expires=mktime(localtime()) + 86400 * 30)
	
	def logout(self):
		return self.makeAnonUser()

class UserService(db.Model):
	name = db.StringProperty(required=True)
	user = db.ReferenceProperty(User, collection_name="services")
	username = db.StringProperty(required=False)
	user_service_id = db.StringProperty(required=True)
	access_token = db.StringProperty(required=True)
	access_token_secret = db.StringProperty(required=False)
	email = db.EmailProperty(required=False)
	picture = db.LinkProperty(required=False)
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
						'access_token_secret': self.access_token_secret,
						'email': self.email,
						'picture': self.picture,
						'url': self.url,
						'created': self.created}

	def json(self):
		return dump_json(self._obj())

	@staticmethod
	def fromJSON(json):
		j = load_json(json)
		return UserService(key_name=j['key'], name=j['name'], user=j['user'], user_service_id=j['user_service_id'], access_token=j['access_token'], access_token_secret=j['access_token_secret'], email=j['email'], picture=j['picture'], url=j['url'], created=j['created'])
