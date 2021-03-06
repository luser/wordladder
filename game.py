#!/usr/bin/env python
from __future__ import with_statement
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from words import getgame, validmove, LevenshteinDistance, difficulty as word_difficulty
from user import User
from time import *
from config import DISTANCE_MATRIX, GAME_WORDLIST, DIFFICULTY_LEVELS, DIFFICULTY_SCORES
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

	@property
	def ladder(self):
		"""
		Return a list of moves that lead from this move to a root move.
		"""
		if hasattr(self, '_ladder'):
			return self._ladder

		self._ladder = [self]
		if self.parent_ and self.parent_.__class__.__name__ == 'Move':
			self._ladder.extend(self.parent_.ladder)

		return self._ladder

	@property
	def isLeaf(self):
		return len(self.children) == 0

	@property
	def isRoot(self):
		return self.parent_.__class__.__name__ == 'Game'

	def _obj(self):
		return {"id": self.id,
						"key": self.key().name(),
						"word": self.word,
						"user": self.user.key().name(),
						"parent": self.parent_,
						"played": self.played,
						"bottom": self.bottom,
						"children": [c.id for c in self.children]}

	# Returns the game in which this move was played.
	@property
	def game(self):
		if hasattr(self, '_game'):
			return self._game

		if self.parent() and self.parent().__class__.__name__ == 'Game':
			self._game = self.parent()
			return self._game
		else:
			return self.parent_.game()

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
	def leaves(self):
		"""
		Return a list of all the leaf nodes in this game's move tree.
		"""
		if hasattr(self, '_leaves'):
			return self._leaves

		self._leaves = []
		for m in self.moves.values():
			if len(m.children) == 0:
				self._leaves.append(m)
		return self._leaves

	@property
	def users(self):
		"""
		Return a dict of user key -> user for all users who have played moves in this game.
		"""
		if hasattr(self, '_users'):
			return self._users

		self._users = {}
		for m in self.moves:
			if self.moves[m].hasValidUser:
				u = self.moves[m].user
				self._users[u.key().name()] = u
		return self._users

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
		self._shortestChainLength = LevenshteinDistance(self.start.word, self.end.word)
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

	@property
	def difficulty(self):
		if hasattr(self, '_difficulty'):
			return self._difficulty
		start_difficulty = word_difficulty(self.start.word)
		end_difficulty = word_difficulty(self.end.word)
		if str(start_difficulty).isdigit() and str(end_difficulty).isdigit():
			# Use actual difficulty ratings if available.
			self._difficulty = int(start_difficulty) + int(end_difficulty)
		# If not, guess based on the Levenshtein distance.
		else:
			self._difficulty = int(LevenshteinDistance(self.start.word, self.end.word))
		return self._difficulty

	@property
	def difficulty_rating(self):
		if hasattr(self, '_difficultyRating'):
			return self._difficultyRating
		total_difficulty = int(sum([word_difficulty(self.start.word), word_difficulty(self.end.word)]))

		# Some special cases
		if int(LevenshteinDistance(self.start.word, self.end.word)) <= 2:
			total_difficulty = max(0, total_difficulty - 2)
		if sorted(self.start.word) == sorted(self.end.word):
			total_difficulty = 0

		score = 4
		for r in DIFFICULTY_SCORES:
			if total_difficulty in r:
				score = DIFFICULTY_SCORES.index(r)
		ratings = {}
		for r in DIFFICULTY_LEVELS:
			ratings[DIFFICULTY_LEVELS[r][0]] = r
		self._difficultyRating = ratings[score]
		return self._difficultyRating

	@property
	def difficulty_multiplier(self):
		return DIFFICULTY_LEVELS[self.difficulty_rating][1]

	@property
	def base_points(self):
		if hasattr(self, '_basePoints'):
			return self._basePoints
		self._basePoints = max(self.difficulty * 10 * self.difficulty_multiplier, 10)
		return self._basePoints

	def scores(self):
		if hasattr(self, '_scores'):
			return self._scores
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

		# Total possible points = base points + short ladder bonus
		short_bonus = self.base_points * (float(winLen) / float(self.difficulty + 4))
		possible_points = self.base_points + int(short_bonus)

		# Divvy up points.
		for u in scores:
			scores[u]['score'] = int(math.floor((float(scores[u]['winMoves']) / float(winLen)) * possible_points))

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
