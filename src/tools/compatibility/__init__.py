# vim: ts=2:sw=2:tw=80:nowrap
import os

def auto_load():
  THISDIR = os.path.dirname( __file__ )
  files = [ # all from_.py files without the .py extension
    f[:-3]  for f in os.listdir( THISDIR )
    if f.startswith('from_') and f.endswith('.py')
  ]
  try:
    for f in files:
      __import__(f, globals=globals(), locals=locals())
  except Exception, e:
    print "could not import converter '" + f + "'"
    print e

# auto load all converters
auto_load()
from register import conversion_path
