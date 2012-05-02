# vim: ts=2:sw=2:tw=80:nowrap
"""
Backend drivers.
Subdirectories of this part of the arbwave package should ONLY contain drivers.
"""

import os

drivers   = dict() # mapping "prefix" to driver module


def add_with_prefix(P,L,C):
  for c in C:
    L[ P + '/' + str(c) ] = c



def get_devices():
  D = dict()
  for d in drivers:
    add_with_prefix( d, D, drivers[d].get_devices() )
  return D

def get_analog_channels():
  D = dict()
  for d in drivers:
    add_with_prefix( d, D, drivers[d].get_analog_channels() )
  return D

def get_digital_channels():
  D = dict()
  for d in drivers:
    add_with_prefix( d, D, drivers[d].get_digital_channels() )
  return D

def get_timing_channels():
  D = dict()
  for d in drivers:
    add_with_prefix( d, D, drivers[d].get_timing_channels() )
  return D

def get_routeable_backplane_signals():
  D = dict()
  for d in drivers:
    add_with_prefix( d, D, drivers[d].get_routeable_backplane_signals() )
  return D


def initialize_device_drivers():
  global drivers
  THISDIR = os.path.dirname( __file__ )

  for D in os.listdir(THISDIR):
    if os.path.isdir( os.path.join(THISDIR,D) ):
      try:
        m = __import__(D,globals=globals(),locals=locals())
        if m.prefix() in drivers:
          raise NameError("Prefix of driver already used: '"+m.prefix()+"'")

        drivers[m.prefix()] = m
        # first test to see if these functions succeed...
        dv = m.get_devices()
        ac = m.get_analog_channels()
        dc = m.get_digital_channels()
        tc = m.get_timing_channels()
        rs = m.get_routeable_backplane_signals()

      except Exception, e:
        print "could not import backend '" + D + "'"
        print e

initialize_device_drivers()
