# vim: ts=2:sw=2:tw=80:nowrap
import os
from importlib import import_module

def auto_load():
  THISDIR = os.path.dirname( __file__ )
  files = [ # all from_.py files without the .py extension
    '.' + f[:-3]  for f in os.listdir( THISDIR )
    if f.startswith('from_') and f.endswith('.py')
  ]
  try:
    for f in files:
      import_module(f, __package__)
  except Exception as e:
    print("could not import converter '" + f + "'")
    print(e)

# auto load all converters
auto_load()
from .register import conversion_path
