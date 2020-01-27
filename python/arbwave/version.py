# vim: ts=2:sw=2:tw=80:nowrap

from subprocess import Popen, PIPE
import os
from bisect import bisect_left
from .tools import compatibility

THIS_DIR = os.path.dirname(__file__)
VERSION_FILE = os.path.join( THIS_DIR, 'VERSION' )
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
  '0.1.8',
  '0.1.9',
  '1.0.0',
  '1.2.0',
]


def version_tuple( v ):
  try:
    vs = v.split('-')
    t = tuple( int(i) for i in vs[0].split('.') )
    if len(vs) > 1:
      try:
        t += ( int(vs[1]), )
      except: pass
    return t
  except:
    return (-1,-1,-1,v)

# sort the file versions by numeric order
tuple_to_ver = lambda t : '.'.join( str(ti) for ti in t )
file_versions.sort( key=version_tuple )


def read_file_version():
  """
  Read (only) the git-version that is stashed in the VERSION_FILE
  """
  if os.path.isfile(VERSION_FILE):
    with open( VERSION_FILE ) as f:
      gv = f.readline()
      return gv.strip()
  else:
    return None

def write_version_file(v=None):
  """
  Write the git-version to the VERSION_FILE
  """
  if v is None:
    v = git_version()
  f = open( VERSION_FILE, 'w' )
  f.write(v)
  f.close()

def _read_git_version():
  try:
    if os.path.isdir('.git'):
      args = {}
    else:
      args = {'cwd' : THIS_DIR}
    with open(os.devnull, 'w') as devnull:
      p = Popen(['git', 'describe'], stdout=PIPE, stderr=devnull, **args)
      out,err = p.communicate()
      if p.returncode:
        raise RuntimeError('no version defined?')
      return out.strip().decode()
  except:
    # no git, let's try using a stashed VERSION file
    v = read_file_version()
    if v is not None:
      return v
    # no git and not VERSION stash, let's make something up based on latest
    # save-file version known
    return DEFAULT_PREFIX + '-' + file_versions[-1]

GIT_VERSION = _read_git_version()
VERSION = GIT_VERSION[GIT_VERSION.find('-')+1:] 
def git_version():
  return GIT_VERSION

def version():
  return VERSION

def prefix():
  return git_version().split('-')[0]

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

def abi_compatible(v0, v1):
  """
  When remote connections to Arbwave objects are made, we will require that they
  are on the same basic version in order to be defined as
  application-binary-interface compatible.  We could do a better job at defining
  compatibility by better versioning rules...
  """
  v0 = version_tuple(v0)
  v1 = version_tuple(v1)
  return v0[:2] == v1[:2]


def main():
  import sys, argparse
  p = argparse.ArgumentParser()
  p.add_argument( '--save', action='store_true',
    help='Store version to '+VERSION_FILE)
  p.add_argument( '--read-file-version', action='store_true',
    help='Read the version stored in '+VERSION_FILE)
  args = p.parse_args()

  v = version()
  if args.save:
    write_version_file(v)
  if args.read_file_version:
    v = read_file_version()
  print(v)

if __name__ == '__main__':
  main()
