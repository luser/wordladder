#!/usr/bin/env python

from words import *
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

class Move(object):
  def __init__(self, word, user, id, parent=None, children=[]):
    self.word = word
    self.user = user
    self.id = id
    self.parent = parent
    if parent:
      parent.children.append(self)
    self.children = children[:]

  def __repr__(self):
    return "Move('%s', '%s', %d, %s, %s)" % (self.word, self.user, self.id, self.parent, self.children)

  def _obj(self):
    return {"id": self.id,
            "word": self.word,
            "user": self.user,
            "children": [c.id for c in self.children]}

  def json(self):
    return dump_json(self._obj())

def processmoves(movedata, moves, i, parent=None):
  md = movedata[str(i)]
  m = Move(md['word'], md['user'], i, parent)
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
      self.moves = {1: Move(self.start, '', 1)}
    self.lastmove = max(m.id for m in self.moves.values())
    self.done = done

  def __repr__(self):
    return "Game('%s', '%s', %s, %s)" % (self.start, self.end, self.done, self.moves)
  
  def __str__(self):
    return "%s-%s" % (self.start, self.end)

  @staticmethod
  def fromJSON(json):
    """Return a Game object from a JSON string. The inverse of the json
    instance method."""
    data = load_json(json)
    moves = {}
    processmoves(data['moves'], moves, 1)
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

    self.lastmove += 1
    newmove = Move(word, user, self.lastmove, m)
    self.moves[self.lastmove] = newmove
    if word == self.end:
      self.done = True
    return (True, '')
