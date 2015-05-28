#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

from subprocess import Popen, PIPE
from os import path
from bisect import bisect_left
from tools import compatibility

THIS_DIR = path.dirname(__file__)
VERSION_FILE = path.join( THIS_DIR, 'VERSION' )
DEFAULT_PREFIX = 'arbwave'

# The file versions are major points in the development history where file
# compatibilty was broken.  Of necessity, only complete version tags should be
# inserted here.  In other words, each version that introduces a backwards
# compatibility issue should be properly tagged and inserted in this list.
file_versions = [
  '0.0.0',
  '0.1.0',
  '0.1.1',
  '0.1.1-15-last-compatibility',
  '0.1.2',
  '0.1.3',
  '0.1.4',
  '0.1.5',
  '0.1.6',
  '0.1.7',
]


def version_tuple( v ):
  try:
    vs = v.split('-')
    t = tuple( int(i) for i in vs[0].split('.') )
    if len(vs) > 1:
      t += ( int(vs[1]), )
    return t
  except:
    return (-1,-1,-1,v)

# sort the file versions by numeric order
tuple_to_ver = lambda t : '.'.join( str(ti) for ti in t )
file_versions.sort( key=version_tuple )


def _read_git_version():
  try:
    if path.isdir('.git'):
      args = {}
    else:
      args = {'cwd' : THIS_DIR }
    p = Popen(['git', 'describe'], stdout=PIPE, **args)
    out,err = p.communicate()
    return out.strip(), True
  except:
    return DEFAULT_PREFIX + '-' + file_versions[-1], False

GIT_VERSION = _read_git_version()
def git_version():
  return GIT_VERSION

def _read_version():
  gv, failover = _read_git_version()
  if failover and path.isfile(VERSION_FILE):
    f = open( VERSION_FILE )
    gv = f.readline()
    f.close()
  if not gv:
    return file_versions[-1]
  return gv[ (gv.find('-')+1): ]


VERSION = _read_version()
def version():
  return VERSION

def prefix():
  return git_version()[0].split('-')[0]


def get_file_version( test_version=None ):
  """
  Return the file version that the test version implements.
  """
  if test_version is None:
    test_version = version()

  if test_version in file_versions:
    return test_version

  file_version_tuples = list( version_tuple(v) for v in file_versions )
  file_version_tuples.insert( 0, (0,0,0) )
  iloc = bisect_left(file_version_tuples, version_tuple(test_version))
  return tuple_to_ver(file_version_tuples[ max(iloc - 1, 0) ])


def conversion_path( test_version ):
  return compatibility.conversion_path(
    get_file_version(test_version),
    get_file_version()
  )


def supported( test_version ):
  return bool( conversion_path(test_version) )


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
