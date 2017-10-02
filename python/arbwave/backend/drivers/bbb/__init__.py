# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Arbwave driver for BeagleBone Black using AFRL firmware/hardware for
experimental control outputs.  Example outputs are arbitrary timing, digital
output, and DDS frequency generation.
"""

from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog
from itertools import chain
import Pyro.core
import Pyro.naming

from ....tools.path import collect_prefix
from ...driver import Driver as Base
from .device import BBB_PYRO_GROUP, create_device


class Driver(Base):
  prefix = 'bbb'
  description = 'Driver for BeagleBone Black w/ AFRL firmware/hardware'
  has_simulated_mode = True

  getProxyForURI = staticmethod(Pyro.core.getAttrProxyForURI)


  def __init__(self, *a, **kw):
    super(Driver,self).__init__(*a, **kw)

    # dict: device path --> Device instance
    self.devices      = dict() # only configured devices

    # dict: device uri  --> Device instance
    self.all_devices  = dict() # both configured and unconfigured

    # dict: user-specified uri --> (objectId, device uri)
    self.extra_uris   = dict()

    if self.simulated:
      import sim
      self._ns = sim.NS()
      self.getProxyForURI = self._ns.getProxyForURI

    else:
      # prepare to discover remote devices
      Pyro.core.initClient()
      try:
        self._ns = Pyro.naming.NameServerLocator().getNS()
      except Pyro.core.NamingError:
        self._ns = None
        info('bbb:  could not find Pyro name server')

    if self._ns:
      self.get_devices()
      info('found %d bbb devices from nameserver', len(self.all_devices))


  def close(self):
    """
    Close connection to each device.
    """
    while self.devices:
      name, device = self.devices.popitem()
      debug( 'closing connection to BeagleBone Black: %s', name )
      device.close()
      del device


  def device_opened(self, device):
    self.devices[str(device)] = device


  def get_devices(self):
    """
    Return list of  devices.  This will return all known devices, whether
    configured or not.

    This list is built from all known device URIs, from the name server (if
    available) and from the set of extra URIs.
    """
    # first all URIs from the name server
    uris = dict() # uri --> objectId
    if self._ns:
      for name, typ in self._ns.list(BBB_PYRO_GROUP):
        if typ != 1: continue # silently skip sub-groups
        objectId = '{}.{}'.format(BBB_PYRO_GROUP,name)
        uris[ str(self._ns.resolve(objectId)) ] = objectId

    # add in all device uris derived from user-specified extra URIs
    uris.update({ uri:oid for uri,oid in self.extra_uris.itervalues() })

    # remove old uris
    for uri in (set(self.all_devices) - set(uris)):
      self.all_devices.pop(uri)

    # now we create device objects for each URI, but do not configure/initialize
    # them.  We do not create new objects if they are found either in
    # self.devices, or in self.all_devices--we simply ensure the objects are
    # listed in self.all_devices.  We also look in self.devices, in case a user
    # has accidentally lost the URI for one device that is already in service.
    active_devices = {d.uri : d for d in self.devices.itervalues()}
    for uri, objectId in uris.iteritems():
      if uri in self.all_devices:
        continue

      if uri in active_devices:
        # copy over the forgotten object
        self.all_devices[uri] = active_devices[uri]

      # no prior device found, so create an un'opened' one
      self.all_devices[uri] = create_device(self, uri, objectId)

    return self.all_devices.values()


  def set_extra_device_URIs(self, uri_list):
    """
    Add list of static URIs to the device discoverer.  Using this interface from
    a global script may be necessary if a Pyro name server is not accessible.
    """
    # ensure these are plain string URIs
    uri_list = set(str(uri) for uri in uri_list)

    # remove old uris
    for uri in (set(self.extra_uris) - uri_list):
      self.extra_uris.pop(uri)

    for uri in uri_list:
      if uri in self.extra_uris:
        # this device has already been added and loaded(?)
        continue

      # need to find device uris from user uris.  The only way I know how to do
      # that is to make/use a connection.
      p = self.getProxyForURI(uri) # makes
      try:
        objectId = p.get_objectId()       # uses
        debug('found bbb::{} object at extra uri: {}', objectId, p.URI)
      except Pyro.core.ProtocolError:
        debug('cannot find bbb::{} object at extra uri: {}', objectId, p.URI)

      # record user-uri  --> device uri
      self.extra_uris[uri] = (objectId, str(p.URI))
      p._release() # release this connection
      del p


  def get_output_channels(self):
    return list(chain(*(
      d.get_output_channels() for d in self.devices.itervalues()
    )))


  def get_timing_channels(self):
    return list(chain(*(
      d.get_timing_channels() for d in self.devices.itervalues()
    )))


  def get_routeable_backplane_signals(self):
    return list(chain(*(
      d.get_routeable_backplane_signals() for d in self.devices.itervalues()
    )))


  def open_required_devices(self, devnames):
    unopened = (set(devnames) - set(self.devices.iterkeys()))
    if unopened:
      # devices configured but not open?; open them
      name_to_device = { str(d):d for d in self.all_devices.values() }
      for devname in unopened:
        debug('bbb: reopening connection to %s', devname)
        name_to_device[devname].open()


  def set_device_config( self, config, channels, signal_graph ):
    debug('bbb.set_device_config(%s, %s, %s)', config, channels, signal_graph)
    # we need to separate channels first by device
    # (configs are already naturally separated by device)
    # in addition, we use collect_prefix to drop the 'bbb/DevX' part of the
    # channel paths
    chans = collect_prefix(channels, 0, 3, 2)

    # devices not configured anymore; remove them
    for devname in (set(self.devices.iterkeys()) - set(config.iterkeys())):
      dev = self.devices.pop(devname)
      dev.close()
      debug('bbb: closed unused device: %s', devname)

    self.open_required_devices(config.iterkeys())

    for d,dev in self.devices.iteritems():
      dev.set_config( config[d] )


  def set_clocks( self, clocks ):
    clocks = collect_prefix(clocks, 0, 3, 3)
    self.open_required_devices(clocks.iterkeys())

    for devname, clks in clocks.iteritems():
      self.devices[devname].set_clocks(clks)


  def set_signals( self, signals ):
    debug('bbb.set_signals(signals=%s)', signals)
    signals = collect_prefix(signals, 0, 3, prefix_list=self.devices)

    self.open_required_devices(signals.iterkeys())

    for devname, sigs in signals.iteritems():
      self.devices[devname].set_signals(sigs)


  def set_static( self, analog, digital ):
    debug('bbb.set_static')
    D =       collect_prefix(digital, 0, 3, 3)
    D.update( collect_prefix(analog,  0, 3, 3) )
    for devname, data in D.iteritems():
      self.devices[ devname ].set_output( data )


  def set_waveforms( self, analog, digital, transitions, t_max, continuous ):
    debug('bbb.set_waveforms')
    D =       collect_prefix(digital, 0, 3, 3)
    D.update( collect_prefix(analog,  0, 3, 3) )

    C = collect_prefix(transitions, 0, 3, 3)
    for d,dev in self.devices.iteritems():
      if d in D or d in C:
        dev.set_waveforms( D.get(d,{}), C.get(d,{}), t_max, continuous )
