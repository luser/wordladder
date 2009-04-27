#!/usr/bin/env python

import web
try:
  # python 2.6, simplejson as json
  from json import dumps as dump_json, loads as load_json
except ImportError:
  try:
    # simplejson moduld
    from simplejson import dumps as dump_json, loads as load_json
  except ImportError:
    # some other json module I apparently have installed
    from json import write as dump_json, read as load_json

class User(object):
	def __init__(self, openid, username=None):
		self.openid = openid
		self.username = username

	def __repr__(self):
		return "User('%s', '%s')" % (self.openid, self.username)

	def __str__(self):
		if self.username:
			return "%s" % (self.username)
		else:
			return "%s" % (self.openid)
	def json(self):
		return dump_json({'openid': self.openid,
				  'username': self.username})
	@staticmethod
	def fromJSON(json):
		j = load_json(json)
		return User(j['openid'], j['username'])

