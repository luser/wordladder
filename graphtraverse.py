#!/usr/bin/env python
# Build a graph of all words in the word list, and determine connectivity
# between all start/end words by traversing the graph.
from __future__ import with_statement

import sys, os, os.path, mmap, pickle
from random import choice, sample, randint
from time import sleep
from config import GAME_WORDLIST, PLAY_WORDLIST, SOLUTION_PATH, DISTANCE_MATRIX

def readwords(f):
  with open(f, "r") as wordlist:
    return [x.rstrip() for x in wordlist.readlines()]

def solutionpath(path, word):
  return os.path.join(path, word[0], word[1], word)

def getmoves(w):
  return readwords(solutionpath(SOLUTION_PATH, w))

def setchoice(s):
  index = randint(0, len(s)-1)
  for i, name in enumerate(s):
    if i == index:
      return name

def find_path(start, end):
  global graph
  queue = [(start, [start])]
  visited = set([start])
  while queue:
    x, path = queue.pop(0)
    for i in graph[x].neighbors:
      if i == end:
        return path + [i]
      if i not in visited:
        visited.add(i)
        queue.append((i, path[:] + [i]))

def find_words(start):
  global graph, wordmap
  queue = [(start, [start])]
  visited = set([start])
  ends = {}
  while queue:
    x, path = queue.pop(0)
    for i in graph[x].neighbors:
      if i not in visited:
        visited.add(i)
        if graph[i].start:
          # save this as an end
          # don't count the first word in the path
          ends[i] = len(path)
        queue.append((i, path[:] + [i]))
  return ends

# read the full set of possible words first
words = readwords(PLAY_WORDLIST)
wordmap =  dict(zip(words, range(len(words))))
gamewords = set(readwords(GAME_WORDLIST))
# separate ids here to index into the distance matrix
gamewordmap =  dict(zip(sorted(gamewords), range(len(gamewords))))

class Node(object):
  def __init__(self, word, start, neighbors):
    """|word| is the word at this node, |start| is True or False:
    True if the word is a start/end node, False if not.
    |neighbors| is a list of integer indices indicating nodes
    which are reachable from this node."""
    self.word = word
    self.start = start
    self.neighbors = neighbors

print "Reading graph...",
graph = {}
GRAPH_PICKLE = "/home/luser/solution.pickle"
if os.path.exists(GRAPH_PICKLE):
  print "(pickled)",
  with open(GRAPH_PICKLE, 'rb') as f:
    graph = pickle.load(f)
else:
  print "(from files)",
  for w, id in wordmap.iteritems():
    graph[id] = Node(w, w in gamewords, [wordmap[n] for n in getmoves(w)])
  with open(GRAPH_PICKLE, 'wb') as f:
    pickle.dump(graph, f, -1)
print "Done"

# No point in keeping this around
words = None

if len(sys.argv) > 1:
  # find shortest path between words on cmdline
  start, end = sys.argv[1:3]
  path = find_path(wordmap[start], wordmap[end])
  print " -> ".join(graph[i].word for i in path)
else:
  # compute shortest path between all word pairs
  # Create a mmapped file to store distance between words
  if not os.path.exists(DISTANCE_MATRIX) or os.stat(DISTANCE_MATRIX).st_size != len(gamewords) * len(gamewords):
    # Fill with 0x0 first if file doesn't exist
    print "Creating empty distance matrix...",
    with open(DISTANCE_MATRIX, 'w') as f:
       for i in xrange(len(gamewords)):
         f.write('\0' * len(gamewords))
    print "Done"
  f = os.open(DISTANCE_MATRIX, os.O_RDWR)
  m = mmap.mmap(f, len(gamewords) * len(gamewords))

  for i, word in enumerate(sorted(gamewords)):
    gwid = gamewordmap[word]
    print "[%5d/%5d] Traversing graph from %s (%d)..." % (i+1, len(gamewords), word, gwid),
    words = find_words(wordmap[word])
    print "Done (max %d)" % max(words.values())

    for wid, pathlen in words.iteritems():
      # need a different kind of index into the connection matrix
      gwid2 = gamewordmap[graph[wid].word]
      m[gwid * len(gamewords) + gwid2] = chr(pathlen)

  print "Done"

  m.flush()
  m.close()
  os.close(f)
