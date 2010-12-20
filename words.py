#!/usr/bin/env python

from __future__ import with_statement
import sys, cPickle
from random import choice, randint

from config import GAME_WORDLIST, PLAY_WORDLIST, DIFFICULTY_TABLE, DIFFICULTY_LEVELS, DIFFICULTY_SCORES

difficulty_table = {}
with open(DIFFICULTY_TABLE, "rb") as dt:
	difficulty_table = cPickle.load(dt)

def randomword(min_difficulty=float('-inf'), max_difficulty=float('inf')):
	"""Return a random word from the dictionary."""
	# lame, should know the length of the file in advance and
	# just pick a random number from that length
	global difficulty_table
	words = []
	for score in difficulty_table:
		if score >= min_difficulty and score <= max_difficulty:
			words.extend(difficulty_table[score])
	word = choice(words)
	return word

def getgame(level = False):
	"""Return two random words (start, end) to be used for a game."""
	if level in DIFFICULTY_LEVELS:
		(s, m) = DIFFICULTY_LEVELS[level]
		t = s
		if s < 4 and randint(0, 100) > 50:
			s += 1
		if t > 0 and randint(0, 100) > 50:
			t -= 1
		start = randomword(min(DIFFICULTY_SCORES[s]), max(DIFFICULTY_SCORES[s]))
		end = randomword(min(DIFFICULTY_SCORES[t]), max(DIFFICULTY_SCORES[t]))
	else:
		start = randomword()
		end = randomword()
	while start == end: # just in case
		end = randomword()
	return (start, end)

def validword(word):
  """Return True if |word| is in the dictionary."""
  return any(x.rstrip().split()[0] == word for x in open(PLAY_WORDLIST, "r"))

def difficulty(word):
	"""Return the difficulty rating of a particular word, if this dictionary contains difficulty ratings."""
	global difficulty_table
	for score in difficulty_table:
		if word in difficulty_table[score]:
			return score
	
	return False

def validwordreason(word):
  """Return (valid, explanation) where |valid| is True or False if
  |word| is a word in the dictionary, and |explanation| is some explanatory
  text otherwise."""
  v = validword(word)
  if v:
    return (True, "")
  return (False, "%s is not a word in the dictionary" % word)

def LevenshteinDistance(s, t):
  """Calculate the Levenshtein distance between |s| and |t| per
  http://en.wikipedia.org/wiki/Levenshtein_distance#The_algorithm """
  m, n = len(s), len(t)
  d = [[0 for x in range(n+1)] for y in range(m+1)]
  # init row, column 0
  for i in range(m+1):
    d[i][0] = i
  for j in range(n+1):
    d[0][j] = j
  for i in range(1, m+1):
    for j in range(1, n+1):
      if s[i-1] == t[j-1]:
        cost = 0
      else:
        cost = 1
      d[i][j] = min(d[i-1][j] + 1, # deletion
                    d[i][j-1] + 1, # insertion
                    d[i-1][j-1] + cost) # substitution
  return d[m][n]

def validmove(start, end):
  """Return (True, '') if |end| is a valid move from the word |start|.
  Otherwise, return (False, 'Reason why this is not a valid move').
  Valid moves entail:
  * Changing one letter
  * Adding or removing one letter
  * Rearranging the existing letters
  In addition, |end| must be a valid word in the dictionary."""
  if start == end:
    # can't just submit the same word
    return (False, "Can't use the same word")
  if len(start) == len(end):
    if sorted(start) == sorted(end):
      # permutation, ok if it's a valid word
      return validwordreason(end)
    if len(filter(lambda x: x[0] != x[1], zip(start, end))) > 1:
      # more than one letter changed
      return (False, "Can't change more than one letter at a time")
    # same length, one letter changed, ok if it's a valid word
    return validwordreason(end)
  if abs(len(start) - len (end)) != 1:
    # more than one letter added/removed, no good
    return (False, "Can't add or remove more than one letter at a time")
  if LevenshteinDistance(start, end) != 1:
    return (False, "Too many letter changes")
  # passed all other tests, ok if it's a valid word
  return validwordreason(end)

if __name__ == '__main__':
  # play a simple console version of word ladder
    start, end = getgame()
    done = False
    words = [start]
    while not done:
      print "%s -> %s" % (start, end)
      s = raw_input(': ')
      valid, reason = validmove(start, s)
      if not valid:
        print "%s -> %s is not a valid move: %s" % (start, s, reason)
        continue
      if s == end:
        done = True
      else:
        words.append(s)
        start = s
    print "Done: %s" % " -> ".join(words)


