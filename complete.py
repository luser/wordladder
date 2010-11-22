#!/usr/bin/env python
# build a list of possible moves for every word in the dictionary
from __future__ import with_statement
from words import *
import sys, os, os.path

try:
  # python 2.6
  from multiprocessing import Pool, cpu_count as cpuCount
except ImportError:
  try:
    # pyprocessing
    from processing import Pool, cpuCount
  except ImportError:
    print >>sys.stderr, "No processing library available! Install pyprocessing or Python 2.6"
    sys.exit(1)

# reopen stdout file descriptor with write mode
# and 0 as the buffer size (unbuffered)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) 
path = sys.argv[1]

def readwords():
  with open(PLAY_WORDLIST, "r") as wordlist:
    return [x.rstrip() for x in wordlist.readlines()]

def writelegalmoves(path, word, words):
  dir = os.path.join(path, word[0], word[1])
  if not os.path.exists(dir):
    os.makedirs(dir)
  fn = os.path.join(dir, word)
  if os.path.exists(fn):
    return
  moves = []
  for x in words:
    if x == word:
      continue
    diff = abs(len(word) - len(x))
    if (diff == 0 and sorted(word) == sorted(x)) or (diff <= 1 and LevenshteinDistance(word, x) == 1):
      moves.append(x)
  with open(fn, 'w') as f:
    if len(moves) != 0:
      f.write("\n".join(moves) + "\n")

def main(*args):
  words = readwords()
  for x in args:
    writelegalmoves(path, x, words)
    sys.stdout.write('.')

if __name__ == '__main__':
  n = cpuCount()
  print "Starting %d processes" % n
  p = Pool(processes=n)
  words = readwords()
  chunk = float(len(words)) / n
  start = 0
  for i in range(n):
    mystart = int(round(start))
    start += chunk
    myend = int(round(start))
    p.apply_async(main, words[mystart:myend])
  p.close()
  p.join()
  print "Done"
