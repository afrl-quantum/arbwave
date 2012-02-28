# vim: ts=2:sw=2:tw=80:nowrap
"""
Backend drivers.
Subdirectories of this part of the arbwave package should ONLY contain drivers.
"""

import os
analog = list()
digital = list()
timing = list()
backplane = list()

def initialize_device_drivers():
  global analog, digital, timing, backplane
  THISDIR = os.path.dirname( __file__ )
  for D in os.listdir(THISDIR):
    if os.path.isdir( os.path.join(THISDIR,D) ):
      try:
        m = __import__(D,globals=globals(),locals=locals())
        analog    += m.get_analog_channels()
        digital   += m.get_digital_channels()
        timing    += m.get_arbitrary_timing_channels()
        backplane += m.get_routeable_backplane_signals()
      except Exception, e:
        print "could not import backend '" + D + "'"
        print e

initialize_device_drivers()
