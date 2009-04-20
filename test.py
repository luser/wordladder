#!/usr/bin/env python
from words import *
import sys

word = sys.argv[1]
for x in open(PLAY_WORDLIST, "r"):
  x = x.rstrip()
  if x == word:
    continue
  diff = abs(len(word) - len(x))
  if (diff == 0 and sorted(word) == sorted(x)) or (diff <= 1 and LevenshteinDistance(word, x) == 1):
    print x
