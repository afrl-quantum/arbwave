# vim: ts=2:sw=2:tw=80:nowrap

import Pyro4

from .. import options

class Driver(object):
  """
  Base driver class

  Drivers should inherit from this class and implement its methods as their main
  point of entry from Arbwave.  Some options can be specified statically as
  static data members of the class:
    prefix:  Should be a short but unique string to identify all components of
             a driver.
    description: Very short textual description of the driver.
    has_simulated_mode: Specifies whether the driver has a simulated modoe
            implemented.
    allow_remote_connection: Specifies whether a driver should allow operation
            in service mode, or whether the driver should only be operated from
            the Local Arbwave instance.  *If* remote operation is permitted, the
            driver _must_ export the various specializations of the functions
            below that are exported here with the @Pyro4.expose decorator.
  """

  prefix = 'undefined'
  description = 'No description'
  has_simulated_mode = False

  # inheriting classes should override this if they are only for local arbwave
  # instances (such as with External driver)
  allow_remote_connection = True

  def __init__(self, host_prefix=None):
    self.host_prefix = ''
    if host_prefix:
      self.prefix = self.format_prefix(host_prefix)
      self.host_prefix = host_prefix + ':'

  @classmethod
  def format_prefix(cls, host_prefix):
    if host_prefix:
      return '{}:{}'.format(host_prefix, cls.prefix)
    else:
      return cls.prefix

  def __del__(self):
    self.close()

  @Pyro4.expose
  @property
  def simulated(self):
    return options.simulated and self.has_simulated_mode

  @Pyro4.expose
  def close(self):
    pass

  def __str__(self):
    return self.prefix

  @Pyro4.expose
  def get_devices(self):
    """
    Return a list of devices connected to this driver.  Note that this should
    return a list of device class instances that are static for the lifetime of
    the driver.
    """
    return []

  @Pyro4.expose
  def get_devices_attrib(self, *attribs, devices=None):
    """
    Return a list of all device attributes connected to this driver.

    An optional list of devices can be given to filter results.
    """
    return {
      d.name:{ai:getattr(d,ai) for ai in attribs}
      for d in self.get_devices()
        if devices is None or d.name in devices
    }

  @Pyro4.expose
  def get_output_channels(self):
    """
    Return a list of all output channels connected to this driver.  This list
    includes analog, digital, and dds output channels of the appropriate output
    channel instances.
    """
    return []

  @Pyro4.expose
  def get_output_channels_attrib(self, *attribs, channels=None):
    """
    Return a list of all output channels connected to this driver.  This list
    includes analog, digital, and dds output channels of the appropriate output
    channel instances.

    An optional list of channels can be given to filter results.
    """
    return {
      str(C):{ai:getattr(C,ai) for ai in attribs}
      for C in self.get_output_channels()
        if channels is None or str(C) in channels
    }

  @Pyro4.expose
  def get_timing_channels(self):
    """
    Return a list of timing channels connected to this driver.  Note that this
    should return a list of timing channel class instances that are static for
    the lifetime of the driver.
    """
    return []

  @Pyro4.expose
  def get_timing_channels_attrib(self, *attribs, channels=None):
    """
    Return a list of all output channels connected to this driver.  This list
    includes analog, digital, and dds output channels of the appropriate output
    channel instances.

    An optional list of channels can be given to filter results.  It should be
    noted that this function will _most likely_ fail unless the channels are
    limited to those that have actually been configured.
    """
    return {
      str(C):{ai:getattr(C,ai) for ai in attribs}
      for C in self.get_timing_channels()
        if channels is None or str(C) in channels
    }

  @Pyro4.expose
  def get_routeable_backplane_signals(self):
    """
    Return a list of signal channels connected to this driver.  Note that this
    should return a list of signal channel class instances that are static for
    the lifetime of the driver.
    """
    return []

  @Pyro4.expose
  def get_routeable_backplane_signals_attrib(self, *attribs, channels=None):
    """
    Return a list of all routeable signals as dictionaries with a 'src' and
    'dest' member.  The src member should be a single string and the dest member
    should be a list of strings.

    An optional list of channels can be given to filter results.
    """
    return [
      {ai:getattr(C,ai) for ai in attribs}
      for C in self.get_routeable_backplane_signals()
        if channels is None or str(C) in channels
    ]

  def get_all_frontend_objects(self):
    """
    Should be used to collect all objects that are to be presented to the front
    panel.  This function is really to support remote objects and is only really
    used for Pyro4 connections.

    This should not be necessary to specialize for inheriting classes.
    This is also not to be exported over Pyro4--it is only used on the service()
    side.
    """

    for D in self.get_devices():
      yield D
    for C in self.get_output_channels():
      yield C
    for C in self.get_timing_channels():
      yield C
    for S in self.get_routeable_backplane_signals():
      yield S

  @Pyro4.expose
  def set_device_config( self, config, channels, signal_graph ):
    if config or channels:
      raise NotImplementedError('Drivers must implement set_device_config')

  @Pyro4.expose
  def set_clocks( self, clocks ):
    """
    Configure output channels on devices from the particular driver from which
    clock signals are generated.
    """
    if clocks:
      raise NotImplementedError('Drivers with clocks must implement set_clocks')

  @Pyro4.expose
  def set_signals( self, signals ):
    if signals:
      raise NotImplementedError(
        'Drivers with routing must implement set_signals'
      )

  @Pyro4.expose
  def set_static( self, analog, digital ):
    if analog or digital:
      raise NotImplementedError(
        'Drivers with analog/digtal channels must implement set_static'
      )

  @Pyro4.expose
  def set_waveforms(self, analog, digital, transitions, t_max, continuous):
    """
    FIXME: show documentation here for all parameters.
    Parameters:
      t_max: time of very last transition for the entire waveform with units of
             time.
    """
    if analog or digital:
      raise NotImplementedError(
        'Drivers with analog/digtal channels must implement set_waveforms'
      )
