#!/usr/bin/env python
#
# Usage: playbot.py <game URL> <solution dir>
from __future__ import with_statement

import sys, httplib, urllib, os.path
from urlparse import urlparse
from random import choice
from time import sleep

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

def readwords(f):
  with open(f, "r") as wordlist:
    return [x.rstrip() for x in wordlist.readlines()]

def solutionpath(path, word):
  return os.path.join(path, word[0], word[1], word)

if len(sys.argv) < 3:
  print >>sys.stderr, "playbot.py <game url> <solution dir>"
  sys.exit(1)

url, dir = sys.argv[1:3]
up = urlparse(url)
headers = {"Accept": "text/json"}
conn = httplib.HTTPConnection(up.netloc)
conn.request("GET", up.path + "?lastmove=0", '', headers)
done = False
while not done:
  response = conn.getresponse()
  if response.status != 200:
    print response.status, response.reason
    sys.exit(1)

  data = load_json(response.read())
  conn.close()
  if 'done' in data:
    done = True
    break
  if 'moves' not in data:
    print "No 'moves' entry in JSON!"
    sys.exit(1)
  # pick a random word in play to play from
  words = [(m['word'], m['id']) for m in data['moves']]
  while True:
    word, moveid = choice(words)
    
    # get possible moves from this word
    potentials = readwords(solutionpath(dir, word))
    while True:
      # pick a random one that's not already in play
      next = choice(potentials)
      if next not in [w for w,i in words]:
        break
      potentials.remove(next)
      if not potentials:
        # all possible moves from this word are in play
        next = None
        break
    if next:
      # found a word to play
      break
  print "Playing %s -> %s" % (word, next)
  # don't go too fast...
  sleep(1)
  params = urllib.urlencode({'moveid': moveid, 'word': next, 'lastmove': 0})
  headers = {"Content-type": "application/x-www-form-urlencoded",
             "Accept": "text/json"}
  conn = httplib.HTTPConnection(up.netloc)
  conn.request("POST", up.path, params, headers)
