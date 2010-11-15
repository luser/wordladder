#!/usr/bin/env python

import web, sys, os, os.path
from web.template import TEMPLATE_BUILTINS
from google.appengine.ext import db

from json import dump_json, load_json

from words import validword
from user import *
from data import *
from facebookoauth import *
from config import HASHKEY

urls = (
  '/', 'index',
  '/new', 'newgame',
  '/new/([^/]*)', 'newgame',
  '/game/([^/]*)', 'game',
  '/user/login', 'login',
  '/user/login/([^/]*)', 'login',
  '/user/logout', 'logout',
  '/user/account', 'account',
  )

app = web.application(urls, globals())
main = app.cgirun()

# stupid incomplete list of builtins!
TEMPLATE_BUILTINS['sorted'] = sorted
render = web.template.render('templates', builtins=TEMPLATE_BUILTINS)

def wantsJSON():
  #TODO: better Accept parsing?
  return 'HTTP_ACCEPT' in web.ctx.environ and web.ctx.environ['HTTP_ACCEPT'].find('json') != -1

def sendJSON(game, lastid, error=None):
  web.header('Content-Type', 'text/plain')
  j = {'moves': [], 'lastmove': game.lastmove}
  if game.done:
    j['done'] = True
    j['winningchain'] = game.winningchain
  for id in sorted(game.moves.keys()):
    if id <= lastid:
      continue
    d = {'id': id, 'word': game.moves[id].word}
    if game.moves[id].parent_:
      d['parent'] = game.moves[id].parent_.id
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

class index:
  def GET(self):
    user = User.currentUser()
    return render.index(Game.all(), user)

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
      g = db.run_in_transaction(creategame, game)
    except GameAlreadyExists:
      raise web.badrequest()
    raise web.seeother("/game/%s" % str(g))

class game:
  def GET(self, game):
    if type(game) is unicode:
      game = game.encode("ascii")
    g = Game.get_by_key_name(game)
    if not g:
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
    user = User.currentUser()
    if type(game) is unicode:
      game = game.encode("ascii")
    d = web.input(moveid=1, word=None, lastmove=None)
    if not d.moveid.isdigit() or d.word is None:
      raise web.badrequest()
    mid = int(d.moveid)
    if type(d.word) is unicode:
      d.word = d.word.encode("ascii")

    try:
      g, valid, reason = db.run_in_transaction(playword, game, mid, d.word, user)
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

class account:
	def POST(self):
		i = web.input('username', return_to='/')
		u = User.currentUser()
		if u:
			if i.username:
				u.setUsername(i.username)
		else:
			return web.redirect('/user/login')
		return web.redirect(i.return_to)
	def GET(self):
		user = User.currentUser()
		if (user.isAnonymous()):
			return render.user(None)
		return render.user(user)

class login:
	def GET(self, service):
		available_services = dict(facebook = facebookOAuth.authorize)
		u = User.currentUser()
		if u:
			web.seeother("/user/account")
		elif service in available_services:
			args = web.input(code = "")
			return available_services[service](args["code"])
		else:
			return render.login()

class logout:
	def GET(self):
		web.setcookie("wl_identity", "", expires=mktime(localtime()) - 86400)
		return web.redirect("/")
