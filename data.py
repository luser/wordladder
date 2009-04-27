# Some simple functions for getting data in and out of the db.
# Everything here should be called via run_in_transaction
# to ensure transactional data safety.

from bsddbdata import run_in_transaction
from game import Game

class GameDoesNotExist(Exception):
  pass

class GameAlreadyExists(Exception):
  pass

def gameFromDB(db, gamename):
  g = db.get(gamename)
  if g is None:
    return None
  return Game.fromJSON(g)

def getallgames(db):
  """Return a dict of gamename -> game object."""
  games = {}
  cur = db.cursor()
  data = cur.first()
  while data:
    games[data[0]] = Game.fromJSON(data[1])
    data = cur.next()
  cur.close()
  return games

def saveGame(db, gamename, game):
  db.put(gamename, game.json())

def playword(db, game, moveid, word, user):
  """Play the word |word| from the word with id |moveid|
  in the game named |game|, for the user |user|.
  Returns (gameobject, valid, reason)."""
  g = gameFromDB(db, game)
  if g is None:
    raise GameDoesNotExist("Game not found")
  valid, reason = g.addmove(moveid, word, user)
  if valid:
    saveGame(db, game, g)
  return g, valid, reason

def deletegame(db, game):
  db.delete(game)

def creategame(db, game=None):
  """Create a game and insert it into the DB. If |game| is not None,
  it must be a string containing start-end. Otherwise, a game
  with random valid words will be created. The game will be saved in
  the data store. Returns the created Game object."""
  if game:
    g = gameFromDB(db, game)
    if g is not None:
      raise GameAlreadyExists("Game already exists")
    start, end = game.split('-')
    g = Game(start=start, end=end)
  else:
    g = None
    g2 = None
    while str(g) == str(g2):
      # ensure that this game doesn't already exist
      g = Game()
      g2 = gameFromDB(db, str(g))
  saveGame(db, str(g), g)
  return g

def currentuser_in_txn(db, openid):
  u = db.get(openid)
  if u:
    return User.fromJSON(u)
  u = User(openid, None)
  db.put(openid, u.json())
  return u

def getcurrentuser(openid):
   return run_in_transaction(currentuser_in_txn, openid, dbname="user.db")
