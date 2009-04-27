#!/usr/bin/env python

import sys
from random import choice

from config import GAME_WORDLIST, PLAY_WORDLIST

def randomword():
  """Return a random word from the dictionary."""
  # lame, should know the length of the file in advance and
  # just pick a random number from that length
  return choice(open(GAME_WORDLIST, "r").readlines()).rstrip()

def getgame():
  """Return two random words (start, end) to be used for a game."""
  start = randomword()
  end = randomword()
  while start == end: # just in case
      end = randomword()
  return (start, end)

def validword(word):
  """Return True if |word| is in the dictionary."""
  return any(x.rstrip() == word for x in open(PLAY_WORDLIST, "r"))

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
      return (validword(end), 'Not a word in the dictionary')
    if len(filter(lambda x: x[0] != x[1], zip(start, end))) > 1:
      # more than one letter changed
      return (False, "Can't change more than one letter at a time")
    # same length, one letter changed, ok if it's a valid word
    return (validword(end), 'Not a word in the dictionary')
  if abs(len(start) - len (end)) != 1:
    # more than one letter added/removed, no good
    return (False, "Can't add or remove more than one letter at a time")
  if LevenshteinDistance(start, end) != 1:
    return (False, "Too many letter changes")
  # passed all other tests, ok if it's a valid word
  return (validword(end), 'Not a word in the dictionary')

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


