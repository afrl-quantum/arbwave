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

  def get_analog_channels(self):
    """
    Return a list of analog channels connected to this driver.  Note that this
    should return a list of analog channel class instances that are static for
    the lifetime of the driver.
    """
    return []

  def get_digital_channels(self):
    """
    Return a list of digital channels connected to this driver.  Note that this
    should return a list of digital channel class instances that are static for
    the lifetime of the driver.
    """
    return []

  def get_timing_channels(self):
    """
    Return a list of timing channels connected to this driver.  Note that this
    should return a list of timing channel class instances that are static for
    the lifetime of the driver.
    """
    return []

  def get_routeable_backplane_signals(self):
    """
    Return a list of signal channels connected to this driver.  Note that this
    should return a list of signal channel class instances that are static for
    the lifetime of the driver.
    """
    return []

  def set_device_config( self, config, channels, signal_graph ):
    if config or channels:
      raise NotImplementedError('Drivers must implement set_device_config')

  def set_clocks( self, clocks ):
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
