#!/usr/bin/env python

import web
import os
from time import *

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
  def __init__(self, openid, username=None, score=0, created=None):
    self.openid = openid
    self.username = username
    self.score = score
    if created:
      if type(created) is str:
        try:
          self.created = strptime(created)
        except ValueError:
          print created + " is not a valid time string."
          raise
      elif type(created) is int or type(created) is float:
        try:
          self.created = localtime(created)
        except ValueError:
          print created + " is not a valid timestamp."
          raise
      elif type(created) is tuple:
        self.created = created
      else:
        raise ValueError
    else:
      self.created = localtime()

  def __repr__(self):
    return "User('%s', '%s', %d, %s)" % (self.openid, self.username, self.score, self.created)

  def __str__(self):
    if self.username:
      return "%s" % (self.username)
    else:
      return "%s" % (self.openid)

  def _obj(self):
    return {'openid': self.openid,
            'username': self.username,
            'score': self.score,
            'created': self.created}

  def isAnonymous(self):
    user = self.openid
    if user.startswith('anon-'):
      return True
    return False

  def json(self):
    return dump_json(self._obj())

  @staticmethod
  def fromJSON(json):
    j = load_json(json)
    return User(j['openid'], j['username'])

def makeAnonUser(db, discard=None):
  anonString = 'anon-'
  maxAnon = 0
  for k in db.keys():
    if k.startswith(anonString):
      parts = k.split('-')
      if int(parts[1]) > maxAnon:
        maxAnon = int(parts[1])
  anonString += str(maxAnon + 1)
  u = User(anonString)
  db.put(anonString, u.json())
  web.setcookie('openid_identity_hash', web.webopenid._hmac(anonString) + ',' + anonString)
  return u

def getSessionScore():
    session_hash = web.cookies().get('ladder_session', '').split(',', 1)
    if len(session_hash) > 1:
        session_hash, session = session_hash
        if session_hash == web.openid._hmac(session):
            del sessions[session]
            web.setcookie('ladder_session', '', expires=-1)
            return sessions[session]['score']
    return None
