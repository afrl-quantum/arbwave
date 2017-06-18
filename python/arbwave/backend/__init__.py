# vim: ts=2:sw=2:tw=80:nowrap
"""
The backend collection includes drivers for each set of devices that is
supported.

This package is also responsible for determining which hardware is available at
the time of initialization.
"""

from logging import info, debug, DEBUG
from . import connection

class Hosts(dict):
  def connect(self, prefix, host ):
    C = connection.factory(prefix, host)
    C.open() # ensure that drivers have been opened
    self[ (prefix,host) ] = C

all_drivers   = dict()  # mapping driver "prefix" to instantiated driver
hosts     = Hosts() # mapping host "(prefix,host)" to connected host

def reconnect( host_defs ):
  """
  Reconnects hosts that have a prefix change or hosts that are new.  Hosts that
  no longer should be connected are disconnected.

  This function also re-populates the "drivers" dictionary with the
  now-currently known drivers.

  Return:  True if changes here imply that the entire backend must be
  reconfigured.  This is the case if a prefix changes, or if the default host
  changes.  Not sure if this is true if a host gets disconnected...
  """

  # first remove known drivers dictionary since we don't want to hang on to any
  # references to objects as hosts are cleared.
  all_drivers.clear()

  new_hosts = set()
  D = host_defs.copy()
  default_prefix = D.pop('__default__', None)
  default_host = D.pop(default_prefix, None)
  if default_host:
    new_hosts.add( ('', default_host) )
  new_hosts.update( { (P,H) for P,H in D.items() } )
  
  old_hosts = set( hosts.keys() )

  # first close out old retired hosts
  for h in (old_hosts - new_hosts):
    hconn = hosts.pop(h)
    info ('removed connection to %s : %s', h, hconn)
    del hconn

  # now create new connection to new hosts
  for h in (new_hosts - old_hosts):
    info ('adding connection to %s', h)
    hosts.connect(*h)

  # finally, repopulate the drivers dictionary
  for C in hosts.values():
    all_drivers.update( { k:d for k,d in C.drivers.items() } )

  # notable change:  hosts have been removed or default has changed
  return bool(old_hosts - new_hosts)


def unload_all():
  # clear all_drivers dict
  all_drivers.clear()
  # close hosts and subsequently drivers
  hosts.clear()


def get_devices():
  D = dict()
  for d in all_drivers.values():
    for c in d.get_devices():
      D[ str(c) ] = c
  return D

def get_output_channels():
  D = dict()
  for d in all_drivers.values():
    for c in d.get_output_channels():
      D[ str(c) ] = c
  return D

def get_timing_channels():
  D = dict()
  for d in all_drivers.values():
    for c in d.get_timing_channels():
      D[ str(c) ] = c
  return D

def get_routeable_backplane_signals():
  L = list()
  for d in all_drivers.values():
    L.extend( d.get_routeable_backplane_signals() )
  return L
