# vim: ts=2:sw=2:tw=80:nowrap
"""
Backend drivers.
Subdirectories of this part of the arbwave package should ONLY contain drivers.
"""

import os
analog    = dict()
digital   = dict()
timing    = dict()
backplane = dict()
drivers   = dict() # mapping "prefix" to driver module


def initialize_device_drivers():
  global analog, digital, timing, backplane, drivers
  THISDIR = os.path.dirname( __file__ )

  def add_with_prefix(P,L,C):
    for c in C:
      L[ P + '/' + str(c) ] = c

  for D in os.listdir(THISDIR):
    if os.path.isdir( os.path.join(THISDIR,D) ):
      try:
        m = __import__(D,globals=globals(),locals=locals())
        if m.prefix() in drivers:
          raise NameError("Prefix of driver already used: '"+m.prefix()+"'")

        drivers[m.prefix()] = m
        ac = m.get_analog_channels()
        dc = m.get_digital_channels()
        tc = m.get_arbitrary_timing_channels()
        rs = m.get_routeable_backplane_signals()

        add_with_prefix( m.prefix(), analog,    ac )
        add_with_prefix( m.prefix(), digital,   dc )
        add_with_prefix( m.prefix(), timing,    tc )
        add_with_prefix( m.prefix(), backplane, rs )

      except Exception, e:
        print "could not import backend '" + D + "'"
        print e

initialize_device_drivers()
