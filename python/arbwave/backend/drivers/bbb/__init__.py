# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Arbwave driver for BeagleBone Black using AFRL firmware/hardware for
experimental control outputs.  Example outputs are arbitrary timing, digital
output, and DDS frequency generation.
"""

from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog
from itertools import chain
import Pyro4

from .... import options
from ....tools.path import collect_prefix
from ....tools import cached
from ...driver import Driver as Base
from .device import BBB_PYRO_GROUP, create_device


class Driver(Base):
  prefix = 'bbb'
  description = 'Driver for BeagleBone Black w/ AFRL firmware/hardware'
  has_simulated_mode = True

  # we will only connect to bbb devices directly
  allow_remote_connection = False

  Proxy = Pyro4.Proxy


  def __init__(self, *a, **kw):
    super(Driver,self).__init__(*a, **kw)

    # dict: device path --> Device instance
    self.devices      = dict() # only configured devices

    # dict: device uri  --> Device instance
    self.all_devices  = dict() # both configured and unconfigured

    # dict: user-specified uri --> (device uri, objectId)
    self.extra_uris   = dict()

    self.resync_ns()
    options.pyro_resync_set.add(self)


  def resync_ns(self):
    if self.simulated:
      from . import sim
      self._ns = sim.NS()
      self.Proxy = self._ns.Proxy

    else:
      # prepare to discover remote devices
      try:
        host, port = None, None

        if options.pyro_ns:
          host_port = options.pyro_ns.split(':')
          host = host_port[0]

          if len(host_port) > 1:
            port = int(host_port[1])

        self._ns = Pyro4.locateNS(host, port)
      except Pyro4.errors.NamingError:
        self._ns = None
        info('bbb:  could not find Pyro4 name server')

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
    return self._devices

  @cached.property(ttl=5)
  def _devices(self):
    """
    Return list of  devices.  This will return all known devices, whether
    configured or not.

    This list is built from all known device URIs, from the name server (if
    available) and from the set of extra URIs.
    """
    debug('bbb: refreshing device list')
    # first all URIs from the name server
    uris = dict() # uri --> objectId
    if self._ns:
      uris.update((uri,name)
        for name, uri in self._ns.list(BBB_PYRO_GROUP).items())

    # add in all device uris derived from user-specified extra URIs
    uris.update(self.extra_uris.values())

    # remove old uris
    for uri in (set(self.all_devices) - set(uris)):
      self.all_devices.pop(uri)

    # now we create device objects for each URI, but do not configure/initialize
    # them.  We do not create new objects if they are found either in
    # self.devices, or in self.all_devices--we simply ensure the objects are
    # listed in self.all_devices.  We also look in self.devices, in case a user
    # has accidentally lost the URI for one device that is already in service.
    active_devices = {d.uri : d for d in self.devices.values()}
    for uri, objectId in uris.items():
      if uri in self.all_devices:
        continue

      if uri in active_devices:
        # copy over the forgotten object
        self.all_devices[uri] = active_devices[uri]
        continue

      # no prior device found, so create an un'opened' one
      dev = create_device(self, uri, objectId)
      if dev is None:
        warn('unknown BBB device type: %s', objectId)
        continue
      if not dev.isopen():
        try:
          # open a temporary connection to ensure that the remote device is
          # compatible
          dev.open()
          dev.close()
        except:
          # not compatible, so don't add
          continue
      self.all_devices[uri] = dev

    return self.all_devices.values()


  def set_extra_device_URIs(self, uri_list):
    """
    Add list of static URIs to the device discoverer.  Using this interface from
    a global script may be necessary if a Pyro4 name server is not accessible.
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
      p = self.Proxy(uri) # makes
      try:
        objectId = p.get_objectId()       # uses
        debug('found bbb::{} object at extra uri: {}', objectId, p._pyroUri)
      except Pyro4.errors.ProtocolError:
        debug('cannot find bbb::{} object at extra uri: {}',
              objectId, p._pyroUri)

      # record user-specified-uri  --> (device-uri, objectId)
      self.extra_uris[uri] = (str(p._pyroUri), objectId)
      p._pyroRelease() # release this connection
      del p


  def get_output_channels(self):
    return list(chain(*(
      d.get_output_channels() for d in self.devices.values()
    )))


  def get_timing_channels(self):
    return list(chain(*(
      d.get_timing_channels() for d in self.devices.values()
    )))


  def get_routeable_backplane_signals(self):
    return list(chain(*(
      d.get_routeable_backplane_signals() for d in self.devices.values()
    )))


  def open_required_devices(self, devnames):
    unopened = (set(devnames) - set(self.devices.keys()))
    if unopened:
      # devices configured but not open?; open them
      name_to_device = { str(d):d for d in self.all_devices.values() }
      for devname in unopened:
        debug('bbb: reopening connection to %s', devname)
        name_to_device[devname].open(take_ownership=True)


  def set_device_config( self, config, channels, signal_graph ):
    debug('bbb.set_device_config(config=%s, channels=%s, signal_graph=%s)',
          config, channels, signal_graph)
    # we need to separate channels first by device
    # (configs are already naturally separated by device)
    # in addition, we use collect_prefix to drop the 'bbb/DevX' part of the
    # channel paths
    chans = collect_prefix(channels, 0, 3, 3)

    # devices not configured anymore; remove them
    for devname in (set(self.devices.keys()) - set(config.keys())):
      dev = self.devices.pop(devname)
      dev.close()
      debug('bbb: closed unused device: %s', devname)

    self.open_required_devices(config.keys())

    for d,dev in self.devices.items():
      dev.set_config( config[d], chans.get(d,{}), signal_graph )


  def set_clocks( self, clocks ):
    clocks = collect_prefix(clocks, 0, 3, 3)
    self.open_required_devices(clocks.keys())

    for devname, clks in clocks.items():
      self.devices[devname].set_clocks(clks)


  def set_signals( self, signals ):
    debug('bbb.set_signals(signals=%s)', signals)
    signals = collect_prefix(signals, 0, 3, prefix_list=self.devices)

    # This only happens if we don't have the bbb device opened.  This helps us
    # ignore this error
    E = [ i for i in signals if i.startswith('External') ]
    for i in E:
      signals.pop(i)

    self.open_required_devices(signals.keys())

    for devname, sigs in signals.items():
      self.devices[devname].set_signals(sigs)


  def set_static( self, analog, digital ):
    debug('bbb.set_static')
    D =       collect_prefix(digital, 0, 3, 3)
    D.update( collect_prefix(analog,  0, 3, 3) )
    for devname, data in D.items():
      self.devices[ devname ].set_output( data )


  def set_waveforms( self, analog, digital, transitions, t_max, continuous ):
    debug('bbb.set_waveforms')
    D =       collect_prefix(digital, 0, 3, 3)
    D.update( collect_prefix(analog,  0, 3, 3) )

    # make it easy to find whether a timing channel is created--we only really
    # need the prefixes and not the rest of the data restructured since we will
    # still pass in all transitions--"C" is just used to help detect whether a
    # device has data to operate on.
    C = collect_prefix(transitions, 0, 3, 3)
    for d,dev in self.devices.items():
      if d in D or d in C:
        # we still pass in all transitions and let timing device split off what
        # it wants itsself
        dev.set_waveforms( D.get(d,{}), transitions, t_max, continuous )
