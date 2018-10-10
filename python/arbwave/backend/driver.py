# vim: ts=2:sw=2:tw=80:nowrap

from .. import options

class Driver(object):
  """Base driver class"""
  _pyro_ = True # For remote connections, this class must use pyro

  prefix = 'undefined'
  description = 'No description'
  has_simulated_mode = False

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

  @property
  def simulated(self):
    return options.simulated and self.has_simulated_mode

  def close(self):
    pass

  def __str__(self):
    return self.prefix

  def get_devices(self):
    """
    Return a list of devices connected to this driver.  Note that this should
    return a list of device class instances that are static for the lifetime of
    the driver.
    """
    return []

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

  def get_output_channels(self):
    """
    Return a list of all output channels connected to this driver.  This list
    includes analog, digital, and dds output channels of the appropriate output
    channel instances.
    """
    return []

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

  def get_timing_channels(self):
    """
    Return a list of timing channels connected to this driver.  Note that this
    should return a list of timing channel class instances that are static for
    the lifetime of the driver.
    """
    return []

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

  def get_routeable_backplane_signals(self):
    """
    Return a list of signal channels connected to this driver.  Note that this
    should return a list of signal channel class instances that are static for
    the lifetime of the driver.
    """
    return []

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

  def set_device_config( self, config, channels, signal_graph ):
    if config or channels:
      raise NotImplementedError('Drivers must implement set_device_config')

  def set_clocks( self, clocks ):
    """
    Configure output channels on devices from the particular driver from which
    clock signals are generated.
    """
    if clocks:
      raise NotImplementedError('Drivers with clocks must implement set_clocks')

  def set_signals( self, signals ):
    if signals:
      raise NotImplementedError(
        'Drivers with routing must implement set_signals'
      )

  def set_static( self, analog, digital ):
    if analog or digital:
      raise NotImplementedError(
        'Drivers with analog/digtal channels must implement set_static'
      )

  def set_waveforms(self, analog, digital, transitions, t_max, continuous):
    if analog or digital:
      raise NotImplementedError(
        'Drivers with analog/digtal channels must implement set_waveforms'
      )
