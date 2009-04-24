#!/usr/bin/env python

import web, sys, os, os.path
try:
  # python 2.6, simplejson as json
  from json import dumps as dump_json
except ImportError:
  try:
    # simplejson moduld
    from simplejson import dumps as dump_json
  except ImportError:
    # some other json module I apparently have installed
    from json import write as dump_json

from words import validword
from data import *
from bsddbdata import run_in_transaction

urls = (
  '/', 'index',
  '/new', 'newgame',
  '/new/([^/]*)', 'newgame',
  '/game/([^/]*)', 'game',
  )

app = web.application(urls, globals())
render = web.template.render('templates/')

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
    j['moves'].append(d)
  if error:
    j['error'] = error
  return dump_json(j)

class index:
  def GET(self):
    return render.index(run_in_transaction(getallgames))

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
    if type(game) is unicode:
      game = game.encode("ascii")
    d = web.input(moveid=1, word=None, lastmove=None)
    if not d.moveid.isdigit() or d.word is None:
      raise web.badrequest()
    mid = int(d.moveid)
    if type(d.word) is unicode:
      d.word = d.word.encode("ascii")

    try:
      g, valid, reason = run_in_transaction(playword, game, mid, d.word, "user")
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

if __name__ == "__main__":
  app.run()
