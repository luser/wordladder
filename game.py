#!/usr/bin/env python

from words import *
from user import User
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

def usertojson(u):
  if type(u) is str:
    return {'openid':None, 'username':u}
  elif type(u) is User:
    return u._obj()
  #FIXME
  return {'openid':None, 'username':'user'}

class Move(object):
  def __init__(self, word, user, id, played=None, parent=None, bottom=False, children=[]):
    self.word = word
    self.user = user
    self.id = id
    self.parent = parent
    self.bottom = bottom
    if played:
      if type(played) is str:
        try:
          self.played = strptime(played)
        except ValueError:
          print played + " is not a valid time string."
          raise
      elif type(played) is int or type(played) is float:
        try:
          self.played = localtime(played)
        except ValueError:
          print played + " is not a valid timestamp."
          raise
      elif type(played) is tuple:
        self.played = played
      else:
        raise ValueError
    else:
      self.played = localtime()
    if parent:
      parent.children.append(self)
    self.children = children[:]

  def __repr__(self):
    return "Move('%s', '%s', %d, %s, %s, %s, %s)" % (self.word, self.user, self.id, self.played, self.parent, self.bottom, [c.id for c in self.children])

  def _obj(self):
    return {"id": self.id,
            "word": self.word,
            "user": usertojson(self.user),
            "played": self.played,
            "bottom": self.bottom,
            "children": [c.id for c in self.children]}

  def json(self):
    return dump_json(self._obj())

  def ts(self):
    return mktime(self.played)

def processmoves(movedata, moves, i, parent=None):
  md = movedata[str(i)]
  if md['user']:
    if type(md['user']) is dict:
      user = User(md['user']['openid'], md['user']['username'])
    else:
      user = User(None, md['user'])
  else:
    user = 'user'
  m = Move(md['word'], user, i, None, parent, md['bottom'])
  moves[i] = m
  for ci in md['children']:
    processmoves(movedata, moves, ci, m)

class Game(object):
  def __init__(self, start=None, end=None, done=False, moves={}):
    if start and end:
      self.start, self.end = start, end
    else:
      self.start, self.end = getgame()
    if moves:
      self.moves = moves
    else:
      self.moves = {1: Move(self.start, '', 1), 2: Move(self.end, '', 2, bottom=True)}
    self.lastmove = max(m.id for m in self.moves.values())
    self.done = done
    if done:
      self.winningchain = self._findwinningchain()
    else:
      self.winningchain = []

  def __repr__(self):
    return "Game('%s', '%s', %s, %s)" % (self.start, self.end, self.done, self.moves)

  def __str__(self):
    return "%s-%s" % (self.start, self.end)

  @staticmethod
  def fromJSON(json):
    """Return a Game object from a JSON string. The inverse of the json
    instance method."""
    data = load_json(json)
    if not 'moves' in data:
      return None
    moves = {}
    processmoves(data['moves'], moves, 1)
    processmoves(data['moves'], moves, 2)
    return Game(data['start'], data['end'], data['done'], moves)

  def json(self):
    """Return a JSON string representing this instance. The inverse of the
    fromJSON static method."""
    return dump_json({"start": self.start,
                      "end": self.end,
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
      mi = mi.parent
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
    newmove = Move(word, user, self.lastmove, None, m, m.bottom)
    self.moves[self.lastmove] = newmove
    if self.done:
      self.winningchain = self._findwinningchain()
    return (True, '')

  def _findwinningchain(self):
    """Return a list of move ids representing the chain that won this
    game, starting from move 1 (the top) and ending at move 2 (the bottom).
    If the game is not finished, returns an empty list."""
    if not self.done:
      return []

    # winning move
    wm = self.moves[self.lastmove]
    # move on the opposite side of the ladder with the same word
    om  = filter(lambda m: m.word == wm.word and m.id != wm.id, self.moves.values())[0]
    m = wm
    l = [wm.id]
    # get chain from the winning move up to the root
    while m.parent:
      m = m.parent
      l.append(m.id)
    m = om
    l2 = [om.id]
    # get chain from the other side up to the root
    while m.parent:
      m = m.parent
      l2.append(m.id)
    # concatenate them
    if wm.bottom:
      l2.reverse()
      l = l2 + l
    else:
      l.reverse()
      l = l + l2
    return l
