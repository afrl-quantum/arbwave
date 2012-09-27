#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

from subprocess import Popen, PIPE
from os import path

VERSION_FILE = path.join( path.dirname(__file__), 'VERSION' )
LAST_KEY_VERSION = 'arbwave-0.1.2'

def git_version():
  try:
    p = Popen(['git', 'describe'], stdout=PIPE)
    out,err = p.communicate()
    return out.strip(), True
  except:
    return LAST_KEY_VERSION, False

def version():
  gv, failover = git_version()
  if failover and path.isfile(VERSION_FILE):
    f = open( VERSION_FILE )
    gv = f.readline()
    f.close()
  if not gv:
    gv = LAST_KEY_VERSION
  return gv[ (gv.find('-')+1):]


def last_key_version():
  V0 = LAST_KEY_VERSION
  return V0[ (V0.find('-')+1): ]


def prefix():
  return git_version()[0].split('-')[0]


def split_version( v ):
  vs = v.split('-')
  t = tuple( int(i) for i in vs[0].split('.') )
  if len(vs) > 1:
    t += ( int(vs[1]), )
  return t

def supported( test_version ):
  v  = split_version( test_version )
  v0 = split_version( last_key_version() ) # drop prefix
  if v0 == v:
    return True
  for i in xrange( min(len(v0), len(v)) ):
    if v0[i] < v[i]:
      return True
  if len(v0) < len(v) and v0 == v[:len(v0)]:
    return True
  return False


if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    if sys.argv[1] == 'save':
      gv = git_version()[0]
      f = open( VERSION_FILE, 'w' )
      f.write(gv)
      f.close()
    elif sys.argv[1] == 'get':
      print version()
