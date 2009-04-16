# build a list of possible moves for every word in the dictionary
from words import *
import sys, os, os.path

path = sys.argv[1]

def writelegalmoves(path, word):
  dir = os.path.join(path, word[0])
  if not os.path.exists(dir):
    os.mkdir(dir)
  f = open(os.path.join(dir, word), 'w')
  for x in open(PLAY_WORDLIST, "r"):
    x = x.rstrip()
    if x == word:
      continue
    if sorted(word) == sorted(x) or LevenshteinDistance(word, x) == 1:
      print >>f, x
  f.close()

for x in open(PLAY_WORDLIST, "r"):
  x = x.rstrip()
  writelegalmoves(path, x)
  sys.stdout.write('.')
print "Done"

