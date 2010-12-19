#!/usr/bin/env python
# Using the connectivity graph, find the shortest path from a word to the nearest 3-letter word.
from __future__ import with_statement

import sys, os, os.path, mmap, cPickle
from random import choice, sample, randint
from config import GAME_WORDLIST, PLAY_WORDLIST

def readwords(f):
	with open(f, "r") as wordlist:
		return [x.rstrip() for x in wordlist.readlines()]

def find_shortest_path(start):
	global graph
	if len(graph[start].word) == 3:
		return 0, graph[start].word
	queue = [(start, [start])]
	visited = set([start])
	while queue:
		x, path = queue.pop(0)
		for i in graph[x].neighbors:
			if len(graph[i].word) == 3:
				return len(path), graph[i].word
			if i not in visited:
				visited.add(i)
				queue.append((i, path[:] + [i]))

# read the full set of possible words first
words = readwords(PLAY_WORDLIST)
wordmap =  dict(zip(words, range(len(words))))
gamewords = set(readwords(GAME_WORDLIST))
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
GRAPH_PICKLE = "./solution.pickle"
if os.path.exists(GRAPH_PICKLE):
	print "(pickled)",
	with open(GRAPH_PICKLE, 'rb') as f:
		graph = cPickle.load(f)
else:
	raise IOError("Graph pickle not found.")
print "Done"

difficulty_table = {}

for i, word in enumerate(sorted(gamewords)):
	print "\t[%5d/%5d] Traversing graph from %s..." % (i+1, len(gamewords), word),
	shortest, endword = find_shortest_path(wordmap[word])
	print "\t\tDone (found path of length %d to %s)." % (shortest, endword)
	if shortest in difficulty_table:
		difficulty_table[shortest].append(word)
	else:
		difficulty_table[shortest] = [word]

difficulty = open("difficulty.dict", 'wb')
cPickle.dump(difficulty_table, difficulty, -1)
difficulty.close()

print "Done."
