# vim: ts=2:sw=2:tw=80:nowrap
"""
The backend collection includes drivers for each set of devices that is
supported.

This package is also responsible for determining which hardware is available at
the time of initialization.
"""

import os

def initialize_device_drivers():
  THISDIR = os.path.dirname( __file__ )
  dirs = [ D  for D in os.listdir(THISDIR)  if os.path.isdir(D) ]
  for D in dirs:
    try:
      m = __import__(D)
    except:
      print 'could not import ', D


initialize_device_drivers()
