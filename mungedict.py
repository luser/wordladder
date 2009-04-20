#!/usr/bin/env python
# given a dictionary and a list of words, produce a reduced dictionary
# with the list of words removed on stdout
from __future__ import with_statement
import sys
from words import *

def readwords(f):
  with open(f, "r") as wordlist:
    return [x.rstrip() for x in wordlist.readlines()]

if len(sys.argv) != 3:
  print >>sys.stderr, "usage: %s <dictionary> <word list>" % sys.argv[0]
  sys.exit(1)

dictwords = readwords(sys.argv[1])
for w in readwords(sys.argv[2]):
  if w in dictwords:
    dictwords.remove(w)
print "\n".join(dictwords)
