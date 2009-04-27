#!/usr/bin/env python

import web, pickle, sys, os, os.path
try:
  # python 2.6, simplejson as json
  from json import dumps as dump_json
except ImportError:
  try:
    # simplejson moduld
    from simplejson import dumps as dump_json
  except ImportError:
    # some other json module I apparently have installed
    from json import write as dump_json
  import openid
except ImportError:
  sys.stderr.write("Couldn't import the OpenID module. Please install python-openid.")
  sys.exit(1)

# not portable, but i don't care
import fcntl

from game import Game
from words import validword
from user import User

try:
  from config import DATA
except ImportError:
  print >>sys.stderr, "You probably didn't copy config.py.dist to config.py and edit the settings correctly. Please do so."
  sys.exit(1)

data = None

def saveData(data):
  f = open(DATA, 'wb')
  # block, but that should be ok
  fcntl.lockf(f, fcntl.LOCK_EX)
  pickle.dump(data, f, -1)
  fcntl.lockf(f, fcntl.LOCK_UN)
  f.close()

def readData():
  f = open(DATA, 'rb')
  fcntl.lockf(f, fcntl.LOCK_SH)
  data = pickle.load(f)
  fcntl.lockf(f, fcntl.LOCK_UN)
  f.close()
  return data

class Data(object):
  def __init__(self):
    self.games = {}
    self.users = {}

if os.path.exists(DATA):
  data = readData()
else:
  data = Data()
  saveData(data)

urls = (
  '/', 'index',
  '/new', 'newgame',
  '/new/([^/]*)', 'newgame',
  '/game/([^/]*)', 'game',
  '/user/login', 'web.webopenid.host',
  '/user/logout', 'web.webopenid.host',
	'/user/account', 'account',
  )

app = web.application(urls, globals())
render = web.template.render('templates/')

def wantsJSON():
  #TODO: better Accept parsing?
  return 'HTTP_ACCEPT' in web.ctx.environ and web.ctx.environ['HTTP_ACCEPT'].find('json') != -1

def sendJSON(game, lastid, error=None):
  web.header('Content-Type', 'text/plain')
  j = {'moves': [], 'lastmove': game.lastmove}
  if game.done:
    j['done'] = True
  for id in sorted(game.moves.keys()):
    if id <= lastid:
      continue
    d = {'id': id, 'word': game.moves[id].word}
    if game.moves[id].parent:
      d['parent'] = game.moves[id].parent.id
    if game.moves[id].user.username:
      d['username'] = game.moves[id].user.username
    else:
      d['username'] = game.moves[id].user.openid
    j['moves'].append(d)
  if error:
    j['error'] = error
  return dump_json(j)

class index:
  def GET(self):
    user = currentUser()
    return render.index(data.games, user)

class newgame:
  def GET(self, game=None):
    if game:
      if game in data.games:
        # already exists
        raise web.badrequest()
      words = game.split('-')
      if len(words) != 2 or (words[0].strip() == '' or words[1].strip == ''):
        # bad format
        raise web.badrequest()
      if not validword(words[0]) or not validword(words[1]):
        # not valid words
        raise web.badrequest()
      g = Game(start=words[0], end=words[1])
    else:
      g = Game()
      while str(g) in data.games:
        g = Game()
    data.games[str(g)] = g
    saveData(data)
    raise web.seeother("/game/%s" % str(g))

class game:
  def GET(self, game):
    if not game in data.games:
      raise web.notfound()
    g = data.games[game]
    if wantsJSON():
      d = web.input(lastmove="1")
      if d.lastmove.isdigit():
        lastmove = int(d.lastmove)
      else:
        lastmove = 1
      return sendJSON(g, lastmove)
    else:
      return render.game(g)

  def POST(self, game):
    user = currentUser()
    if not game in data.games:
      raise web.notfound()
    g = data.games[game]
    d = web.input(moveid=1, word=None, lastmove=None)
    if not d.moveid.isdigit() or d.word is None:
      raise web.badrequest()
    mid = int(d.moveid)
    if not mid in g.moves:
      raise web.badrequest()
    json = wantsJSON()
    if json:
      if d.lastmove is None or not d.lastmove.isdigit():
        raise web.badrequest()
    valid, reason = g.addmove(mid, d.word, user)
    if not valid:
      if not json:
        return render.play(g, d.word, reason)
      else:
        return sendJSON(g, int(d.lastmove), reason)
    saveData(data)
    if not json:
      raise web.seeother("/game/%s" % str(g))
    else:
      return sendJSON(g, int(d.lastmove))

def currentUser():
  openid = web.openid.status()
  if not openid:
    user = None
  else :
    if not openid in data.users:
      data.users[openid] = User(openid, None)
      saveData(data)
    user = data.users[openid]
  return user

class account:
  def POST(self):
    user = currentUser()
    i = web.input('username', return_to='/')
    if user:
      user.username = i.username
      data.users[user.openid] = user
      saveData(data)
    else:
      raise web.badrequest()
    return web.redirect(i.return_to)
  def GET(self):
    user = currentUser()
    return render.user(user)

if __name__ == "__main__":
  app.run()
