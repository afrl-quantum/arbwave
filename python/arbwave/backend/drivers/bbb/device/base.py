# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Logical device driver for the BeagleBone Black using AFRL firmware/hardware.
"""

from logging import debug, info
from physical import unit

from .....version import version as arbwave_version, abi_compatible
from ....device import Device as Base


class Device(Base):
  """
  The Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """


  def __init__(self, driver, uri, devname):
    super(Device,self).__init__(name='{}/{}'.format(driver, devname))
    self.hostid = devname.split('/')[0]
    self.driver = driver
    self.uri    = uri
    self.proxy  = None
    self.is_continuous = None
    self.t_max = 0.0 * unit.s


  def __del__(self):
    self.close()


  def close(self):
    if self.isopen():
      self.proxy._pyroRelease()
      del self.proxy
      self.proxy = None


  def isopen(self):
    return bool(self.proxy)


  def open(self):
    """
    Create the proxy to the remote object and add the device to the drivers list
    of devices.  This function is called when a device is added to the devices
    tab of the configuration dialog.
    """
    if self.isopen():
      raise RuntimeError('bbb.Device({}): Connection already opened'.format(self))

    self.proxy = self.driver.Proxy(self.uri)

    ## test and assert version compatibility
    if not abi_compatible(arbwave_version(), self.proxy.get_version()):
      self.close()
      raise RuntimeError(
        'bbb.Device({}): remote AFRL/BeagleBone Black ({}) Arbwave version is incompatible'
        .format(self, self.uri)
      )

    # now tell the driver that this device is configured
    self.driver.device_opened(self)

    debug('found BeagleBone Black+AFRL device: %s', self)


  def set_config(self, config, channels, signal_graph):
    """
    Set the internal configuration for the board. This
    does not include the sequence specification or the backplane routing.

    :param config: the configuration dictionary to be applied, compare
                   get_config_template()
    :param channels: Dictionary of channels configured for this device.  Each
                   value returned is actually a dictionary including max, min
                   output values for the channel and also the order of the
                   channel in the channel list on the gui.
    :param signal_graph: directed graph of signal routing
    """
    pass


  def get_output_channels(self):
    return []


  def get_timing_channels(self):
    return []


  def get_routeable_backplane_signals(self):
    return []


  def set_clocks(self, clocks):
    """
    Configure output channels on devices from the particular driver from which
    clock signals are generated.
    """
    raise RuntimeError(
      'bbb.Device({}):  does not have clocks channels'.format(self))


  def set_signals(self, signals):
    """
    Set the backplane routing info.

    :param signals: a dict of { (src, dest) : config_dict} where src and
                    dest are both paths
    """
    raise RuntimeError(
      'bbb.Device({}):  does not have routeable signals'.format(self))


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set the output waveforms for the AFRL/BeagleBone Black device.

    :param waveforms:
      a dict('channel': {<wfe-path>: (<encoding>, [(t1, val1), (t2, val2)])})
                      (see gui/plotter/digital.py for format)
                      where wfe-path means waveform element path, referring to
                      the unique identifier of the specific waveform element a
                      particular set of values refers to.
    :param clock_transitions: a dict('channel': { 'dt': dt, 
                              'transitions': iterable})
                              (see processor/engine/compute.py for format)
    :param t_max: the maximum duration of any channel in units of time.
    :param continuous: bool of continuous or single-shot mode
    """
    debug('bbb.Device(%s).set_waveforms(waveforms=%s, clock_transitions=%s, ' \
          't_max=%s, continuous=%s)',
          self, waveforms, clock_transitions, t_max, continuous)
    self.is_continuous = bool(continuous)
    self.set_waveforms_impl(waveforms, clock_transitions, t_max)
    self.t_max = t_max


  def start(self):
    """
    Start the sequence: arm the board.
    """
    if self.is_continuous is None:
      # we don't have any waveforms, so skip starting
      return
    debug('bbb.Device(%s).start()', self)
    self.proxy.exec_waveform(1 if not self.is_continuous else 0)


  def wait(self):
    """
    Wait for the sequence to finish.
    """
    debug('bbb.Device(%s).wait()', self)
    if self.is_continuous:
      raise RuntimeError('cannot wait for continuous waveform to finish')

    reps = self.proxy.waitfor_waveform(timeout = self.t_max.coeff*2)
    debug('bbb.Device(%s).wait(): dds finished %d iterations', self, reps)


  def stop(self):
    """
    Forceably stop any running sequence.
    """
    debug('bbb.Device(%s).stop()', self)
    self.proxy.stop()
    self.is_continuous = None
