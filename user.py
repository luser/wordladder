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
		return {'key': self.key(),
						'username': self.username,
            'created': mktime(self.created)}

	def isAnonymous(self):
		user = self.username
		if user.startswith('anon-'):
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
				return None
			if (hmac.new(HASHKEY, parts[0], hashlib.sha1).hexdigest() == parts[1]):
				user = User.get_by_key_name(key_names=parts[0])
				if user:
					return user
				else:
					web.setcookie("wl_identity", "", expires=mktime(localtime()) - 86400)
					return None
			else:
				raise web.badrequest()
		else:
			return None

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
		return {'key': self.key(),
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
  return User()
  #fix this all
  anonString = 'anon-'
  maxAnon = 0
  for k in db.keys():
    if k.startswith(anonString):
      parts = k.split('-')
      if int(parts[1]) > maxAnon:
        maxAnon = int(parts[1])
  anonString += str(maxAnon + 1)
  u = User('none', anonString)
  db.put(anonString, u.json())
  web.setcookie('wl_identity', 'anonymous-' + anonString + '/' + hmac.new(HASHKEY, anonString, hashlib.sha1), expires=mktime(localtime()) + 30 * 86400)
  return u

def getSessionScore():
    session_hash = web.cookies().get('ladder_session', '').split(',', 1)
    if len(session_hash) > 1:
        session_hash, session = session_hash
        if session_hash == hmac.new(session, '', hashlib.sha1()):
            del sessions[session]
            web.setcookie('ladder_session', '', expires=-1)
            return sessions[session]['score']
    return None
