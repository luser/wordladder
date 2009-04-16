from words import *
import sys

test = sys.argv[1]
for x in open(PLAY_WORDLIST, "r"):
  x = x.rstrip()
  if x == test:
    continue
  if sorted(test) == sorted(x) or LevenshteinDistance(test, x) == 1:
    print x
