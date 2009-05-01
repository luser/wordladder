#!/usr/bin/env python

import web, sys, os, os.path, minifb
try:
  # python 2.6, simplejson as json
  from json import dumps as dump_json
except ImportError:
  try:
    # simplejson module
    from simplejson import dumps as dump_json
  except ImportError:
    # some other json module I apparently have installed
    from json import write as dump_json
try:
  import openid
except ImportError:
  print >>sys.stderr, "Couldn't import the OpenID module. Please install python-openid."
  sys.exit(1)

from words import validword
from user import User
from data import *
from bsddbdata import run_in_transaction

urls = (
  '/', 'index',
  '/new', 'newgame',
  '/new/([^/]*)', 'newgame',
  '/game/([^/]*)', 'game',
  '/user/login', 'web.webopenid.host',
  '/user/logout', 'web.webopenid.host',
  '/user/account', 'account',  '/fb/', 'fb_index',
  '/fb/add', 'fb_add',
  '/fb/remove', 'fb_remove',
  '/fb/new', 'fb_newgame',
  '/fb/new/([^/]*)', 'fb_newgame',
  '/fb/game/([^/]*)', 'fb_game',
  )

app = web.application(urls, globals())
render = web.template.render('templates/')

_FbApiKey = '605bd3fd951affff9fd423bf6ecccf18'
_FbSecret = minifb.FacebookSecret('a89f16f3d4605b4e920430234d1a7b29')
_CanvasURL = 'http://apps.facebook.com/wordladder/'
_RegURL = 'http://www.facebook.com/add.php?api_key=' + _FbApiKey

web.template.Template.globals['_CanvasURL'] = _CanvasURL

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
    if game.moves[id].bottom:
      d['bottom'] = True
    if game.moves[id].user:
      if game.moves[id].user.username:
        d['username'] = game.moves[id].user.username
      else:
        d['username'] = game.moves[id].user.openid
    j['moves'].append(d)
  if error:
    j['error'] = error
  return dump_json(j)

def minival(inp):
  args = minifb.validate(_FbSecret,inp)
  if args['added']==0:
      return """<fb:redirect url="%s" />""" % _RegURL
  return args

class index:
  def GET(self):
    user = currentUser()
    return render.index(run_in_transaction(getallgames), user)

class newgame:
  def GET(self, game=None):
    if game:
      if type(game) is unicode:
        game = game.encode("ascii")
      words = game.split('-')
      if len(words) != 2 or (words[0].strip() == '' or words[1].strip == ''):
        # bad format
        raise web.badrequest()
      if not validword(words[0]) or not validword(words[1]):
        # not valid words
        raise web.badrequest()
    try:
      g = run_in_transaction(creategame, game)
    except GameAlreadyExists:
      raise web.badrequest()
    raise web.seeother("/game/%s" % str(g))

class game:
  def GET(self, game):
    if type(game) is unicode:
      game = game.encode("ascii")
    g = run_in_transaction(gameFromDB, game)
    if not game:
      raise web.notfound()
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
    if type(game) is unicode:
      game = game.encode("ascii")
    d = web.input(moveid=1, word=None, lastmove=None)
    if not d.moveid.isdigit() or d.word is None:
      raise web.badrequest()
    mid = int(d.moveid)
    if type(d.word) is unicode:
      d.word = d.word.encode("ascii")

    try:
      g, valid, reason = run_in_transaction(playword, game, mid, d.word, user)
    except GameDoesNotExist:
      raise web.notfound()

    json = wantsJSON()
    if json:
      if d.lastmove is None or not d.lastmove.isdigit():
        d.lastmove = '1'
    if not valid:
      if not json:
        return render.play(g, d.word, reason)
      else:
        return sendJSON(g, int(d.lastmove), reason)
    if not json:
      raise web.seeother("/game/%s" % str(g))
    else:
      return sendJSON(g, int(d.lastmove))

def currentUser():
  openid = web.openid.status()
  if not openid:
    #TODO: support anonymous users
    return None
  return getcurrentuser(openid)

def setcurrentUsername(username):
  openid = web.openid.status()
  if not openid:
    #TODO: support anonymous users
    return None
  return setusername(openid, username)

class account:
  def POST(self):
    i = web.input('username', return_to='/')
    try:
      setcurrentUsername(i.username)
    except UserDoesNotExist:
      raise web.badrequest()
    return web.redirect(i.return_to)
  def GET(self):
    user = currentUser()
    return render.user(user)
    
class fb_add:
  def POST(self):
    args = minival(web.input())
    # Do something after the application is added
    return """<fb:redirect url="%s" />""" % _CanvasURL

class fb_remove:
  def POST(self):
    args = minival(web.input())
    # Do something after the application is removed
    return """<fb:redirect url="%s" />""" % _CanvasURL

class fb_newgame:
  def POST(self, game=None):
    args = minival(web.input())
    if game:
      if type(game) is unicode:
        game = game.encode("ascii")
      words = game.split('-')
      if len(words) != 2 or (words[0].strip() == '' or words[1].strip == ''):
        # bad format
        raise web.badrequest()
      if not validword(words[0]) or not validword(words[1]):
        # not valid words
        raise web.badrequest()
    try:
      g = run_in_transaction(creategame, game)
    except GameAlreadyExists:
      raise web.badrequest()
    #raise web.seeother("/fb/game/%s" % str(g))
    return """<fb:redirect url="%sgame/%s" />""" % (_CanvasURL, str(g))

class fb_game:
  def POST(self, game):
    args = minival(web.input())
    if type(game) is unicode:
      game = game.encode("ascii")
    g = run_in_transaction(gameFromDB, game)
    if not game:
      raise web.notfound()
    if wantsJSON():
      d = web.input(lastmove="1")
      if d.lastmove.isdigit():
        lastmove = int(d.lastmove)
      else:
        lastmove = 1
      return sendJSON(g, lastmove)
    else:
      return render.fb_game(g)

if __name__ == "__main__":
  app.run()
