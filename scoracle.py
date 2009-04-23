#!/usr/bin/env python
from __future__ import with_statement

import sys, os, mmap, cgi
from config import GAME_WORDLIST, DISTANCE_MATRIX

def readwords(f):
  with open(f, "r") as wordlist:
    return [x.rstrip() for x in wordlist.readlines()]

def minpath(start, end):
  gamewords = readwords(GAME_WORDLIST)
  gamewordmap =  dict(zip(gamewords, range(len(gamewords))))
  swid, ewid = gamewordmap[start], gamewordmap[end]
  f = os.open(DISTANCE_MATRIX, os.O_RDWR)
  m = mmap.mmap(f, len(gamewordmap) * len(gamewordmap))
  return ord(m[swid * len(gamewordmap) + ewid])
  m.close()
  os.close(f)

if __name__ == '__main__':
  try:
    form = cgi.FieldStorage()
    if not (form.has_key("start") and form.has_key("end")):
      raise Exception
    start, end = form.getfirst("start"), form.getfirst("end")
    print "Content-Type: text/plain\n"
    print minpath(start, end)
  except:
    print "400 Bad Request\n"
