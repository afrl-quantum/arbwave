# vim: ts=2:sw=2:tw=80:nowrap
"""
Backend drivers.
Subdirectories of this part of the arbwave package should ONLY contain drivers.
"""

import os, traceback, logging
from logging import debug, DEBUG
from ... import options

class Drivers(dict):
  def __init__(self):
    super(Drivers,self).__init__()
    self.__dict__ = self
class Hosts(dict):
  def __init__(self):
    super(Hosts,self).__init__()
    self.default = 'local'
    self['localhost'] = dict( prefix='local' )
drivers   = Drivers() # mapping "prefix" to instantiated driver
hosts     = Hosts()

def reconnect( host_defs ):
  D = host_defs.copy()
  D.pop( '__default__' )
  new_hosts = set( D.values() )
  old_hosts = set( hosts.keys() )

  # first close out old retired hosts
  for h in (old_hosts - new_hosts):
    hconn = hosts.pop(h)
    print 'removed connection to "'+h+'": ', hconn

  # now create new connection to new hosts
  for h in (new_hosts - old_hosts):
    print 'adding connection to', h
    hosts[h] = 'New connection'

  # hosts have been either added or removed? if so, this is a notable change
  return new_hosts != old_hosts


def get_devices():
  D = dict()
  for d in drivers.values():
    for c in d.get_devices():
      D[ str(c) ] = c
  return D

def get_analog_channels():
  D = dict()
  for d in drivers.values():
    for c in d.get_analog_channels():
      D[ str(c) ] = c
  return D

def get_digital_channels():
  D = dict()
  for d in drivers.values():
    for c in d.get_digital_channels():
      D[ str(c) ] = c
  return D

def get_timing_channels():
  D = dict()
  for d in drivers.values():
    for c in d.get_timing_channels():
      D[ str(c) ] = c
  return D

def get_routeable_backplane_signals():
  L = list()
  for d in drivers.values():
    L.extend( d.get_routeable_backplane_signals() )
  return L


def unload_all():
  while drivers:
    name, d = drivers.popitem()
    debug( 'closing driver: %s', name )
    try:
      d.close()
    except:
      traceback.print_exc()
      print 'driver not cleanly closed: ', name


def initialize_device_drivers():
  global drivers
  THISDIR = os.path.dirname( __file__ )

  for D in os.listdir(THISDIR):
    if os.path.isdir( os.path.join(THISDIR,D) ):
      try:
        m = __import__(D,globals=globals(),locals=locals())
        if m.prefix() in drivers:
          raise NameError("Prefix of driver already used: '"+m.prefix()+"'")

        if m.is_simulated() != options.simulated:
          raise NotImplementedError(
            'Cannot load driver in simulated mode: ' + m.prefix()
          )

        m.init()
        drivers[m.prefix()] = m
        # first test to see if these functions succeed...
        dv = m.get_devices()
        ac = m.get_analog_channels()
        dc = m.get_digital_channels()
        tc = m.get_timing_channels()
        rs = m.get_routeable_backplane_signals()

      except Exception, e:
        print "could not import backend '" + D + "'"
        if logging.root.getEffectiveLevel() <= (DEBUG-1):
          debug( e )
          debug( traceback.format_exc() )

initialize_device_drivers()
