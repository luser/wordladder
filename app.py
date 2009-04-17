#!/usr/bin/env python

import web, pickle, sys, os, os.path
import simplejson as json
# not portable, but i don't care
import fcntl

from game import Game

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
  '/game/([^/]*)', 'game',
  '/game/([^/]*)/play', 'play',
  )

app = web.application(urls, globals())
render = web.template.render('templates/')

def wantsJSON():
  #TODO: better Accept parsing?
  return 'HTTP_ACCEPT' in web.ctx.environ and web.ctx.environ['HTTP_ACCEPT'].find('json') != -1

def sendJSON(game, lastid, error=None):
  web.header('Content-Type', 'text/plain')
  j = {'moves': [], 'lastmove': game.lastmove}
  for id in sorted(game.moves.keys()):
    if id <= lastid:
      continue
    j['moves'].append({'id': id, 'word': game.moves[id].word,
                       'parent': game.moves[id].parent.id})
  if error:
    j['error'] = error
  return json.dumps(j)

class index:
  def GET(self):
    return render.index(data.games)

class newgame:
  def GET(self):
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
      print >>sys.stderr, "lastmove: %d" % lastmove
      return sendJSON(g, lastmove)
    else:
      return render.game(g)

class play:
  def POST(self, game):
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
    valid, reason = g.addmove(mid, d.word, 'user')
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
  
if __name__ == "__main__":
  app.run()
