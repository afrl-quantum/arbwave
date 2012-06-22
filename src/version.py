#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

from subprocess import Popen, PIPE
from os import path

VERSION_FILE = path.join( path.dirname(__file__), 'VERSION' )
UNKNOWN_VERSION = 'arbwave-UNKNOWN'

def git_version():
  try:
    p = Popen(['git', 'describe'], stdout=PIPE)
    out,err = p.communicate()
    return out.strip()
  except:
    return UNKNOWN_VERSION

def version():
  gv = git_version()
  if gv == UNKNOWN_VERSION and path.isfile(VERSION_FILE):
    f = open( VERSION_FILE )
    gv = f.readline()
    f.close()
  if not gv:
    gv = UNKNOWN_VERSION
  return gv[ (gv.find('-')+1):]

def prefix():
  return git_version().split('-')[0]


if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    if sys.argv[1] == 'save':
      gv = git_version()
      f = open( VERSION_FILE, 'w' )
      f.write(gv)
      f.close()
    elif sys.argv[1] == 'get':
      print version()
