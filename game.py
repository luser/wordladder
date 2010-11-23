#!/usr/bin/env python
from __future__ import with_statement
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from words import getgame, validmove, LevenshteinDistance
from user import User
from time import *
from config import DISTANCE_MATRIX, GAME_WORDLIST
import sys, os, math

from json import dump_json, load_json

class Move(db.Model):
	id = db.IntegerProperty(required=True)
	word = db.StringProperty(required=True)
	user = db.ReferenceProperty(User, collection_name="moves")
	parent_ = db.SelfReferenceProperty()
	bottom = db.BooleanProperty(default=False)
	played = db.DateTimeProperty(auto_now_add=True)

	def __str__(self):
		return self.word

	@property
	def children(self):
		"""
		Return a list of moves that are direct children of this move.
		"""
		if hasattr(self, '_children'):
			return self._children

		self._children = []
		q = db.GqlQuery('SELECT * FROM Move WHERE ANCESTOR IS :1 AND parent_ = :2', self.parent_key(), self.key())
		for m in q:
			self._children.append(m)

		return self._children

	def _obj(self):
		return {"id": self.id,
						"key": self.key().name(),
						"word": self.word,
						"user": self.user.key().name(),
						"parent": self.parent_,
						"played": self.played,
						"bottom": self.bottom,
						"children": [c.id for c in self.children]}

	@property
	def hasValidUser(self):
		# BUG http://code.google.com/p/googleappengine/issues/detail?id=426
		self._hasValidUser = False
		try:
			u = self.user
			if u:
				self._hasValidUser = True
		except datastore_errors.Error:
			self._hasValidUser = False
		return self._hasValidUser

	def json(self):
		return dump_json(self._obj())

def processmoves(movedata, moves, i, parent=None):
	md = movedata[str(i)]
	if 'user' in md and md['user']:
		user = User.get(md['user'])
	else:
		user = 'user'
	if 'played' in md:
		played = md['played']
	else:
		played = None
	m = Move(id=i, word=md['word'], user=user, played=played, parent_=parent, bottom=md['bottom'])
	moves[i] = m
	for ci in md['children']:
		processmoves(movedata, moves, ci, m)

class Game(db.Model):
	done = db.BooleanProperty(default=False)
	start = db.ReferenceProperty(Move, collection_name="start_set")
	end = db.ReferenceProperty(Move, collection_name="end_set")
	#XXX: do this more intelligently?
	lastmove = db.IntegerProperty(required=True)

	@staticmethod
	def new(start, end):
		"""
		Create and return a new Game object. Optionally provide
		a start and end word for the game. If not provided random
		words will be selected.
		"""
		g = Game(key_name="%s-%s" % (start, end), lastmove=2)
		start_move = Move(parent=g, word=start, id=1)
		start_move.put()
		g.start = start_move
		end_move = Move(parent=g, word=end, id=2, bottom=True)
		end_move.put()
		g.end = end_move
		g.put()
		return g

	@property
	def moves(self):
		"""
		Return a dict of move id -> move for all moves in this game.
		"""
		if hasattr(self, '_moves'):
			return self._moves

		self._moves = {}
		q = db.GqlQuery('SELECT * FROM Move WHERE ANCESTOR IS :1', self.key())
		for m in q:
			self._moves[m.id] = m
		return self._moves

	@property
	def winningchain(self):
		"""
		Return a list of moves representing the chain of words
		that won the game.
		"""
		if not self.done:
			return []
		if not hasattr(self, '_winningchain'):
			self._winningchain = self._findwinningchain()
		return self._winningchain

	def shortestChainLength(self):
		if hasattr(self, '_shortestChainLength'):
			return self._shortestChainLength
		with open(GAME_WORDLIST, "r") as wordlist:
			gamewords = [x.rstrip() for x in wordlist.readlines()]
		gamewordmap =  dict(zip(gamewords, range(len(gamewords))))
		swid, ewid = gamewordmap[self.start.word], gamewordmap[self.end.word]
		f = open(DISTANCE_MATRIX, 'r')
		f.seek(swid * len(gamewordmap) + ewid, os.SEEK_SET)
		self._shortestChainLength = ord(f.read(1))
		f.close()
		return self._shortestChainLength

	def __repr__(self):
		return "Game('%s', '%s', %s)" % (self.start.word,
																		 self.end.word,
																		 self.done)

	def __str__(self):
		return "%s-%s" % (self.start.word, self.end.word)

	def json(self):
		"""
		Return a JSON string representing this instance.
		"""
		return dump_json({"start": self.start.word,
											"end": self.end.word,
											"done": self.done,
											"moves": dict((str(i), m._obj()) for i,m in self.moves.iteritems())})

	def addmove(self, fromid, word, user):
		if self.done:
			return (False, "Game is finished")
		if fromid not in self.moves:
			return (False, "Invalid word ID")
		m = self.moves[fromid]
		# make sure this word isn't already a child here
		if any(c.word == word for c in m.children):
			return (False, "Your word has already been played from that word")
		# make sure this word hasn't already been played in this chain
		mi = m
		while mi is not None:
			if mi.word == word:
				return (False, "Your word has already been played in this chain")
			mi = mi.parent_
		# see if it's a valid move (valid word, valid transition)
		valid, reason = validmove(m.word, word)
		if not valid:
			return (False, reason)

		# see if this completes a chain
		wmap = dict((m.word, m) for id, m in self.moves.iteritems())
		if word in wmap:
			if wmap[word].bottom != m.bottom:
				# completed a chain
				self.done = True

		self.lastmove += 1
		newmove = Move(parent=self,
									 word=word,
									 user=user,
									 parent_=m,
									 id=self.lastmove,
									 bottom=m.bottom)
		newmove.put()
		self.moves[self.lastmove] = newmove
		return (True, '')
	
	def finish(self):
		scores = self.scores()
		for u in scores:
			user = User.get_by_key_name(u)
			if user:
				user.score += int(scores[u]['score'])
				user.put()
		self.winningchain
		return True

	def _findwinningchain(self):
		"""Return a list of move ids representing the chain that won this
		game, starting from move 1 (the top) and ending at move 2 (the bottom).
		If the game is not finished, returns an empty list."""
		if not self.done:
			return []

		# winning move
		wm = self.moves[self.lastmove]
		# move on the opposite side of the ladder with the same word
		om	= filter(lambda m: m.word == wm.word and m.id != wm.id, self.moves.values())[0]
		m = wm
		l = [wm.id]
		# get chain from the winning move up to the root
		while m.parent_:
			m = m.parent_
			l.append(m.id)
		m = om
		l2 = [om.id]
		# get chain from the other side up to the root
		while m.parent_:
			m = m.parent_
			l2.append(m.id)
		# concatenate them
		if wm.bottom:
			l2.reverse()
			l = l2 + l
		else:
			l.reverse()
			l = l + l2
		return l

	def scores(self):
		if hasattr(self, '_scores'):
			return self._scores
		short = self.shortestChainLength()
		win = self._findwinningchain()
		winLen = len(win) - 2 # Subtract start and end moves.

		scores = {}
		
		# Find out how many moves each contributor to the winning chain contributed.
		for m in win:
			m = self.moves[m]
			if m.hasValidUser:
				u = str(m.user.key().id_or_name())
				if u in scores:
					scores[u]['winMoves'] += 1
				else:
					scores[u] = {'username': str(m.user), 'picture': m.user.picture, 'score': 0, 'winMoves': 1}

		# Figure out base points based on difficulty.
		# TODO: This is kind of arbitrary.
		# TODO: If we start using different dictionaries for different skill levels, incorporate that here.
		difficulty = (float(short) + float(LevenshteinDistance(self.start.word, self.end.word))) / float(10)

		# Determine base points based on difficulty.
		basePoints = math.floor(2 * float(difficulty)) * 10

		# Divvy up base points.
		for u in scores:
			scores[u]['score'] = math.floor((float(scores[u]['winMoves']) / float(winLen)) * basePoints)

		# Divvy up performance points.
		for u in scores:
			scores[u]['score'] += math.floor((float(scores[u]['winMoves']) / float(winLen)) * ((4 * difficulty * float(short)) - (winLen - short)))
			scores[u]['score'] = int(scores[u]['score'])

		self._scores = scores
		return scores

	# Returns a simple version of the scores array, suitable for use by javascript.
	@property
	def score(self):
		if not self.done:
			return {}
		if not hasattr(self, '_scores'):
			self.scores()
		return self._scores
