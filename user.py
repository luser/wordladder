#!/usr/bin/env python

import web

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
