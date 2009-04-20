#!/usr/bin/env python
# look for word pairs whose only legal move is each other
from __future__ import with_statement
import sys, os, os.path

def readwords(f):
  with open(f, "r") as wordlist:
    return [x.rstrip() for x in wordlist.readlines()]

def solutionpath(path, word):
  return os.path.join(path, word[0], word[1], word)

if len(sys.argv) != 3:
  print "usage: %s <dictionary> <solution dir>" % sys.argv[0]
  sys.exit(1)

dictionary, dir = sys.argv[1:3]
usedwords = set()
for word in readwords(dictionary):
  moves = readwords(solutionpath(dir, word))
  if len(moves) > 1:
    # only interested in single-move words right now
    continue
  if word in usedwords:
    # already seen
    continue
  othermoves = readwords(solutionpath(dir, moves[0]))
  if len(othermoves) == 1:
    if othermoves[0] != word:
      print "WTF, %s -> %s -> %s ?" % (word, moves[0], othermoves[0])
      continue
    usedwords.add(word)
    usedwords.add(moves[0])
    print "%s\n%s" % (word, moves[0])
