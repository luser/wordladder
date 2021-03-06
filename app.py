#!/usr/bin/env python

import web, sys, os, os.path
from web.template import TEMPLATE_BUILTINS
from google.appengine.ext import db

from json import dump_json, load_json

from words import validword
from user import *
from session import *
from data import *
from config import *

urls = (
	'/', 'index',
	'/new', 'newgame',
	'/new/([^/]*)', 'newgame',
	'/game/([^/]*)', 'game',
	'/user/login/([^/]*)', 'login',
	'/user/update/([^/]*)', 'update',
	'/user/remove/([^/]*)', 'remove',
	'/user/usephoto/([^/]*)', 'usephoto',
	'/user/logout', 'logout',
	'/user/account', 'account',
	)

app = web.application(urls, globals())
main = app.cgirun()

# stupid incomplete list of builtins!
TEMPLATE_BUILTINS['sorted'] = sorted
TEMPLATE_BUILTINS['dump_json'] = dump_json
TEMPLATE_BUILTINS['currentUser'] = User.currentUser
render = web.template.render('templates', builtins=TEMPLATE_BUILTINS, base='layout')

def wantsJSON():
	#TODO: better Accept parsing?
	return 'HTTP_ACCEPT' in web.ctx.environ and web.ctx.environ['HTTP_ACCEPT'].find('json') != -1

def sendJSON(game, lastid, error=None):
	web.header('Content-Type', 'text/plain')
	j = {'moves': [], 'lastmove': game.lastmove}
	if game.done:
		j['done'] = True
		j['winningchain'] = game.winningchain
		j['scores'] = game.score
	for id in sorted(game.moves.keys()):
		if id <= lastid:
			continue
		d = {'id': id, 'word': game.moves[id].word}
		if game.moves[id].parent_:
			d['parent'] = game.moves[id].parent_.id
		if game.moves[id].bottom:
			d['bottom'] = True
		if game.moves[id].user:
			d['userid'] = game.moves[id].user.key().name()
			if game.moves[id].user.key().name() not in [game.moves[m].user.key().name() for m in game.moves if game.moves[m].hasValidUser and m < lastid]:
				if game.moves[id].user.username:
					d['username'] = game.moves[id].user.username
				else:
					d['username'] = "Guest"
				d['picture'] = game.moves[id].user.picture
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
			if '-' in game:
				words = game.split('-')
				if len(words) != 2 or (words[0].strip() == '' or words[1].strip == ''):
					# bad format
					raise web.badrequest()
				if not validword(words[0]) or not validword(words[1]):
					# not valid words
					raise web.badrequest()
			elif game not in DIFFICULTY_LEVELS:
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
			user = User.currentUser()
			return render.game(g, user)

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

		if g.done:
			g.finish()

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
		i = web.input('username')
		u = User.currentUser()
		if u:
			if i.username:
				u.setUsername(i.username)
		else:
			return web.redirect('/user/login')
		return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
	def GET(self):
		user = User.currentUser()
		return render.user(user, SERVICES)

class login:
	def GET(self, service):
		user = User.currentUser()
		if user and not user.isAnonymous() and not service in SERVICES:
			web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
		elif service in SERVICES:
			args = web.input(code = '', oauth_token = '', oauth_verifier = '')
			return getServiceFunction(service, 'login')(args)
		else:
			return render.login()

class logout:
	def GET(self):
		User.currentUser().logout()
		return web.seeother(User.currentSession().getKey('redirect') and 1 or '/')
		
class update:
	def GET(self, service):
		user = User.currentUser()
		if user and not user.isAnonymous() and not service in SERVICES:
			return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
		elif service in SERVICES and service in [s.name for s in user.services]:
			for s in user.services:
				if s.name == service:
					if getServiceFunction(service, 'update')(s.access_token, s.access_token_secret):
						User.currentSession().addMessage('info', 'Successfully updated ' + service + ' profile.')
					else:
						User.currentSession().addMessage('info', 'Failed to update ' + service + ' profile.')
					return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
		return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')

class remove:
	def GET(self, service):
		user = User.currentUser()
		if user and not user.isAnonymous() and not service in SERVICES:
			return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
		elif service in SERVICES and service in [s.name for s in user.services]:
			for s in user.services:
				if s.name == service:
					s.delete()
					User.currentSession().addMessage('info', 'Successfully deleted ' + service + ' profile.')
					return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
		return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')

class usephoto:
	def GET(self, service):
		user = User.currentUser()
		if user and not user.isAnonymous() and not service in SERVICES:
			return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
		elif service in SERVICES and service in [s.name for s in user.services]:
			for s in user.services:
				if s.name == service:
					user.picture = s.picture
					user.put()
					User.currentSession().addMessage('info', 'Using ' + s.name + ' picture as user icon.')
					return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
		return web.seeother(User.currentSession().getKey('redirect') and 1 or '/user/account')
			
def getServiceFunction(serviceName, functionType):
	if not serviceName in SERVICES:
		return None
	
	moduleName = SERVICES[serviceName]['module']
	if moduleName not in sys.modules:
		__import__(moduleName)

	className = SERVICES[serviceName]['class']
	c = getattr(sys.modules[moduleName], className)

	if not c:
		return None

	f = getattr(c, SERVICES[serviceName][functionType])
	if f:
		return f
	return None
