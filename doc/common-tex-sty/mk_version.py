#!/usr/bin/env python
from subprocess import Popen, PIPE
from os import path

COMMON_DIR=path.dirname(__file__)
MANDIR = path.join( COMMON_DIR, path.pardir, 'manual' )

def get_version():
  try:
    git = Popen(['git','describe'], stdout=PIPE)
    name,version = git.communicate()[0].strip().split('-',1)
    git = Popen(['git','log','--format=%ci','-1'],stdout=PIPE)
    revdate = git.communicate()[0].split()[0]

    return version, revdate
  except:
    return '0.1.0', '2012-08-01'

def get_man_version():
  try:
    git = Popen(['git','log','--format=%ci','-1',MANDIR],stdout=PIPE)
    mandate = git.communicate()[0].split()[0]
    return mandate
  except:
    return '2012-08-01'

def write_latex(fname='arbwave-version.sty'):
  version, revdate = get_version()
  mandate = get_man_version()

  f = open( path.join(COMMON_DIR, fname), 'w' )
  f.write(
    '\\edef\\revision{{{version}}}\n'   \
    '\\edef\\revdate{{{revdate}}}\n'    \
    '\\edef\\mandate{{{mandate}}}\n'    \
    .format(**locals())
  )
  f.close()

write_latex()
