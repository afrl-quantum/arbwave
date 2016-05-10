#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import unittest, os
from .. import expand

def e(tc, s,r):
  res = " ".join(expand.expand_braces(s))
  if res != r:
    print "*** FAILED: '%s'" % s
  tc.assertEqual( r, res )

class Expand(unittest.TestCase):
  def test_expand_braces(self):
    e(self,'hello', 'hello')
    e(self,'{hello,world}', 'hello world')
    e(self,'x{a,b}', 'xa xb')
    e(self,'x{a,b,c}y', 'xay xby xcy')
    e(self,'A{1,2,3}B-C{4,5,6}D', 'A1B-C4D A1B-C5D A1B-C6D A2B-C4D A2B-C5D A2B-C6D A3B-C4D A3B-C5D A3B-C6D')
    e(self,'a{b,<{c,d}>}e', 'abe a<c>e a<d>e')
    e(self,'{1..10x}', '1..10x')
    e(self,'{x1..10}', 'x1..10')
    e(self,'{1..10}', '1 2 3 4 5 6 7 8 9 10')
    e(self,'a{1..10}b', 'a1b a2b a3b a4b a5b a6b a7b a8b a9b a10b')
    e(self,'{a,b}1..10', 'a1..10 b1..10')
    e(self,'{a,9..13,b}', 'a 9..13 b')
    e(self,'<{a,{9..13},b}>', '<a> <9> <10> <11> <12> <13> <b>')
    e(self,'electron_{n,{pt,eta,phi}[{1,2}]}', 'electron_n electron_pt[1] electron_pt[2] electron_eta[1] electron_eta[2] electron_phi[1] electron_phi[2]')
    e(self,'Myfile{1,3..10}.root', 'Myfile1.root Myfile3..10.root')
    e(self,'Myfile{1,{3..10}}.root', 'Myfile1.root Myfile3.root Myfile4.root Myfile5.root Myfile6.root Myfile7.root Myfile8.root Myfile9.root Myfile10.root')
    e(self,'{pre,,post}amble', 'preamble amble postamble')
    e(self,'amble{a,b,}}', 'amblea} ambleb} amble}')
    e(self,'{1..10}', '1 2 3 4 5 6 7 8 9 10')
    e(self,'{a..j}', 'a b c d e f g h i j')
    e(self,'{10..1}', '10 9 8 7 6 5 4 3 2 1')
    e(self,'{j..a}', 'j i h g f e d c b a')
    e(self,'{10..-10}', '10 9 8 7 6 5 4 3 2 1 0 -1 -2 -3 -4 -5 -6 -7 -8 -9 -10')
