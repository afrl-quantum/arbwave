#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import gtk_tools
import var_tools

from gtk_tools import load_file


if __name__ == '__main__':
  vdict = {
    'A' : 'a',
    'B' : 'b',
    'C' : 'c',
    'D' : 'd',
  }

  F = open('testvars.py', 'w')
  writevars(F, vdict)
  F.close()

  F = open('testvars.py')
  vdictnew = readvars(F)
  F.close()

  print 'original variables: \n'
  print vdict
  print 'saved/reread variables: \n'
  print vdictnew

