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
  global graph, wordmap
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
  ends = set()
  while queue:
    x, path = queue.pop(0)
    for i in graph[x].neighbors:
      if i not in visited:
        visited.add(i)
        if graph[i].start:
          # save this as an end
          ends.add(i)
          sys.stdout.write('.')
        queue.append((i, path[:] + [i]))
  return ends

# read the full set of possible words first
words = readwords(PLAY_WORDLIST)
wordmap =  dict(zip(words, range(len(words))))
gamewords = set(readwords(GAME_WORDLIST))
# separate ids here to index into the distance matrix
gamewordmap =  dict(zip(gamewords, range(len(gamewords))))

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
  with open(GRAPH_PICKLE, 'rb') as f:
    graph = pickle.load(f)
else:
  for w, id in wordmap.iteritems():
    graph[id] = Node(w, w in gamewords, [wordmap[n] for n in getmoves(w)])
  with open(GRAPH_PICKLE, 'wb') as f:
    pickle.dump(graph, f, -1)

print "Done"

# No point in keeping this around
words = None

while True:
  start = setchoice(gamewords)
  print "Traversing graph from %s" % start,
  words = find_words(wordmap[start])
  print "Done"
  print "%s has %d reachable words:" % (start, len(words))
  if len(words) > len(gamewords)/2:
    # well-connected
    with open("connected.dict", 'w') as f:
      # add the start back in
      words.add(wordmap[start])
      f.write("\n".join(graph[i].word for i in sorted(words))+"\n")
    break
  sleep(1)

print "Done"

# Create a mmapped file to store distance between words
# Fill with 0xFF first
# with open(DISTANCE_MATRIX, 'w') as f:
#   for i in xrange(len(gamewords) * len(gamewords)):
#     f.write('\xFF')

# print "Traversing graph..."
# f = os.open(DISTANCE_MATRIX, os.O_RDWR)
# m = mmap.mmap(f, len(gamewords) * len(gamewords))
# for w in gamewords:
#   gid = gamewordmap[w]
#   id = wordmap[w]
#   dft(graph, id, gid, m, [], set())
# print "Done"
# m.flush()
# m.close()
# os.close(f)
