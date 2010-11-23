#!/usr/bin/env python

import web
import os
import hmac
import hashlib
import pickle
from time import *
from user import *

from json import dump_json, load_json
from google.appengine.ext import db
from config import HASHKEY

class Session(db.Model):
	user = db.ReferenceProperty(None, collection_name="session") # TODO: Should be User, not None, but fuck that.
	created = db.DateTimeProperty(required=True, auto_now_add=True)
	accessed = db.DateTimeProperty(required=True, auto_now=True)

	def __str__(self):
		s = "Session %s" % self.key().name()
		for p in self.params:
			s += "\n\t" + str(p)
		return s

	def _obj(self):
		return {'key': self.key().name(),
						'user': self.user.key(),
						'created': self.created,
            'accessed': mktime(self.accessed)}

	def json(self):
		return dump_json(self._obj())

	@staticmethod
	def fromJSON(json):
		j = load_json(json)
		return Session(key_name=j['key'], user=j['user'], created=j['created'], accessed=j['accessed'])

	def setKey(self, name, value):
		params = self.params
		for param in params:
			if param.name == name:
				param.value = value
				return True
		p = SessionParam(asession=self, name=name, value=value)
		p.put()
		return True

	def getKey(self, name):
		params = self.params
		for param in params:
			if param.name == name:
				return param.value
		return None

	def deleteKey(self, name):
		params = self.params
		for param in params:
			if param.name == name:
				param.delete()
				return True
		return False

	def get_and_delete(self, name):
		value = self.getKey(name)
		if value:
			self.deleteKey(name)
			return value
		return None

	def addMessage(self, type, message):
		current = self.getMessages(type)
		current.append(message)
		current = pickle.dumps(current)
		return self.setKey(type+'messages', current)

	def getMessages(self, type):
		current = self.getKey(type+'-messages')
		if current:
			current = pickle.loads(current)
		else:
			current = []
		return current

	def clearMessages(self, type):
		return self.deleteKey(type+'-messages')

class SessionParam(db.Model):
	asession = db.ReferenceProperty(Session, collection_name="params")
	name = db.StringProperty(required=True)
	value = db.TextProperty(required=False)
	created = db.DateTimeProperty(required=True, auto_now_add=True)

	def __str__(self):
		if self.name and self.value:
			return "%s: %s" % (self.name, self.value)
		else:
			return "%s: (empty)" % self.name

	def _obj(self):
		return {'key': self.key().name(),
						'session': self.session.key(),
						'name': self.name,
						'value': self.value,
						'created': self.created}

	def json(self):
		return dump_json(self._obj())

	@staticmethod
	def fromJSON(json):
		j = load_json(json)
		return SessionParam(key_name=j['key'], session=j['session'], name=j['name'], value=j['value'], created=j['created'])
