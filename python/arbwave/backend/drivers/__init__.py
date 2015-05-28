# vim: ts=2:sw=2:tw=80:nowrap
"""
Backend drivers.
Subdirectories of this part of the arbwave package should ONLY contain drivers.
"""

import traceback
from logging import debug, DEBUG
from .. import connection

class Drivers(dict):
  def __init__(self):
    super(Drivers,self).__init__()
    self.__dict__ = self

class Hosts(dict):
  def __init__(self):
    super(Hosts,self).__init__()
    self.default = None

  def __setitem__(self, host, prefix):
    if host == 'localhost':
      C = connection.Local()
    else:
      C = connection.Remote(host)
    super(Hosts,self).__setitem__(host, dict( prefix=prefix, connection=C ))

drivers   = Drivers() # mapping "prefix" to instantiated driver
hosts     = Hosts()

def reconnect( host_defs ):
  old_default = hosts.default
  D = host_defs.copy()
  hosts.default = D.pop( '__default__' )
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
  return new_hosts != old_hosts or old_default != hosts.default


def unload_all():
  while drivers:
    name, d = drivers.popitem()
    debug( 'closing driver: %s', name )
    try:
      d.close()
    except:
      traceback.print_exc()
      print 'driver not cleanly closed: ', name



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
