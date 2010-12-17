#!/usr/bin/env python
# given a dictionary and a list of words with frequency information, produce
# a list of words with frequency scores, from 1 (very frequent) to 5 (very
# infrequent).
from __future__ import with_statement
import sys
from words import *

def readdict(f):
  with open(f, "r") as wordlist:
    return [x.rstrip() for x in wordlist.readlines()]

def readfreq(f):
	freq = {}
	with open(f, "r") as freqlist:
		freqlines = freqlist.readlines()	
	
	for l in freqlines:
		f, w, d1, d2 = l.strip().split()
		if w in freq:
			freq[w] += int(f);
		else:
			freq[w] = int(f);
	for w in freq:
		if freq[w] > 250:
			freq[w] = 1
		elif freq[w] > 50 and freq[w] < 250:
			freq[w] = 2
		elif freq[w] > 25 and freq[w] < 50:
			freq[w] = 3
		elif freq[w] > 10 and freq[w] < 25:
			freq[w] = 4
		else:
			freq[w] = 5
	return freq

if len(sys.argv) != 3:
  print >>sys.stderr, "usage: %s <dictionary> <word frequency list>" % sys.argv[0]
  sys.exit(1)

dictwords = readdict(sys.argv[1])
freqwords = readfreq(sys.argv[2])

outwords = []

for w in dictwords:
	if w in freqwords:
		outwords.append(w + ' ' + str(freqwords[w]))
	else:
		if w.endswith(('s','y','r')) and w[:-1] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-1]]))
		elif w.endswith(('ed','er','es')) and w[:-1] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-1]]))
		elif w.endswith(('ed','er','es','ic','ly')) and w[:-2] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-2]]))
		elif w.endswith(('ly','ar','al','ty')) and w[:-1] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-1]]))
		elif w.endswith('ic') and w[:-2] + 'y' in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-2] + 'y']))
		elif w.endswith('ily') and w[:-3] + 'y' in freqwords:
			outwords. append(w + ' ' + str(freqwords[w[:-3] + 'y']))
		elif w.endswith(('ing','eds','ers','est')) and w[:-3] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-3]]))
		elif w.endswith('ing') and w[-5:-4] == w[-4:-3] and w[:-5] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-5]]))
		elif w.endswith(('eds','ers','est')) and w[:-2] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-2]]))
		elif w.endswith('ing') and w[:-3] + 'e' in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-3] + 'e']))
		elif w.endswith('ier') and w[:-3] + 'y' in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-3] + 'y']))
		elif len(w) >= 4 and w.endswith('iest') and w[:-4] + 'y' in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[:-4] + 'y']))
		elif w.startswith('a') and w[1:] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[1:]]))
		elif w.startswith(('be','co','de','en','ex','in','il','ir','re','un','up')) and w[2:] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[2:]]))
		elif w.startswith(('con','non','nor','pre','per')) and w[3:] in freqwords:
			outwords.append(w + ' ' + str(freqwords[w[3:]]))
		else:
			outwords.append(w + ' 5')
		
print "\n".join(outwords)
