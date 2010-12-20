# Some simple functions for getting data in and out of the db.
# Everything here should be called via run_in_transaction
# to ensure transactional data safety.

from google.appengine.ext import db
from game import Game
from words import getgame
from user import *
from config import DIFFICULTY_LEVELS

class GameDoesNotExist(Exception):
	pass

class GameAlreadyExists(Exception):
	pass

class UserDoesNotExist(Exception):
	pass

def getallgames(db):
	"""Return a dict of gamename -> game object."""
	games = {}
	cur = db.cursor()
	data = cur.first()
	while data:
		g = Game.fromJSON(data[1])
		if g:
			games[data[0]] = g
		data = cur.next()
	cur.close()
	return games

def saveGame(game):
	game.put()

def playword(game, moveid, word, user):
	"""Play the word |word| from the word with id |moveid|
	in the game named |game|, for the user |user|.
	Returns (gameobject, valid, reason)."""
	g = Game.get_by_key_name(game)
	if g is None:
		raise GameDoesNotExist("Game not found")
	valid, reason = g.addmove(moveid, word, user)
	if valid:
		saveGame(g)
	return g, valid, reason

def deletegame(db, game):
	db.delete(game)

def creategame(game=None):
	"""Create a game and insert it into the DB. If |game| is not None,
	it must be a string containing start-end. Otherwise, a game
	with random valid words will be created. The game will be saved in
	the data store. Returns the created Game object."""
	if not game:
		while True:
			# Find a game that doesn't exist
			start, end = getgame()
			game = "%s-%s" % (start, end)
			if Game.get_by_key_name(game) is None:
				break
	elif '-' in game:
		start, end = game.split('-')
	elif game in DIFFICULTY_LEVELS:
		while True:
			start, end = getgame(game)
			game = "%s-%s" % (start, end)
			if Game.get_by_key_name(game) is None:
				break

	if Game.get_by_key_name(game) is not None:
		raise GameAlreadyExists("Game already exists")
	return Game.new(start, end)

def currentuser_in_txn(db, openid):
	u = db.get(openid)
	if u:
		return User.fromJSON(u)
	u = User(openid, None)
	score = getSessionScore()
	if score:
		u.score += score
	db.put(openid, u.json())
	return u

def getcurrentuser(openid):
	return run_in_transaction(currentuser_in_txn, openid, dbname="user.db")

def setusername_in_txn(db, openid, username):
	u = db.get(openid)
	if not u:
		raise UserDoesNotExist("That user does not exist")

	user = User.fromJSON(u)
	user.username = username
	db.put(openid, user.json())
	return user

def setusername(openid, username):
	 return run_in_transaction(setusername_in_txn, openid, username, dbname="user.db")

def web_host(with_proto=True, with_port=True):
	url = ''

	if with_proto:
		url += web.ctx.env['wsgi.url_scheme']+'://'

	if web.ctx.env.get('HTTP_HOST'):
		url += web.ctx.env['HTTP_HOST']
	else:
		url += web.ctx.env['SERVER_NAME']

	if with_port and ':' not in url:
		if web.ctx.env['wsgi.url_scheme'] == 'https':
			if web.ctx.env['SERVER_PORT'] != '443':
				url += ':' + web.ctx.env['SERVER_PORT']
		else:
			if web.ctx.env['SERVER_PORT'] != '80':
				url += ':' + web.ctx.env['SERVER_PORT']

	return url
