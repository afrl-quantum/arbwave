# vim: ts=2:sw=2:tw=80:nowrap

import logging
import Pyro4

from .device import Device
from . import capabilities
from ...driver import Driver as Base
from ....tools.path import collect_prefix


class Driver(Base):
  prefix      = 'vp'
  description = 'Viewpoint Driver'
  has_simulated_mode = True
  boards_to_probe = range(10)

  def __init__(self, *a, **kw):
    super(Driver,self).__init__(*a, **kw)
    # hook the simulated library if needed
    if self.simulated:
      logging.debug( 'viewpoint.sim: installing simulated library' )
      from . import sim
      import viewpoint as vp
      self._old_dio64 = vp.clib.dio64
      vp.board.dio64 = vp.clib.dio64 = sim.DIO64()
      self.boards_to_probe = range(1)

    # mapping from board index to device
    self.devices = dict()

    logging.info( 'probing for first %d viewpoint boards...',
      len(self.boards_to_probe) )
    for i in self.boards_to_probe:
      try:
        d = Device( self, i )
      except:
        break
      self.devices[str(d)] = d
    logging.info( 'found %d viewpoint boards', len(self.devices) )

    self.digital_channels = capabilities.get_digital_channels(self.devices)
    self.timing_channels = capabilities.get_timing_channels(self.devices)
    self.signals = capabilities.get_routeable_backplane_signals(self.devices)

  @Pyro4.expose
  def close(self):
    """Close all devices and uninitialize everything"""
    while self.devices:
      devname, dev = self.devices.popitem()
      logging.debug( 'closing viewpoint device: %s', devname )
      dev.close()
      del dev

    if self.simulated:
      logging.debug( 'viewpoint.sim: restoring real library' )
      # restore the vp lib
      import viewpoint as vp
      vp.board.dio64 = vp.clib.dio64 = self._old_dio64

  @Pyro4.expose
  def get_devices(self):
    return self.devices.values()

  @Pyro4.expose
  def get_output_channels(self):
    return self.digital_channels

  @Pyro4.expose
  def get_timing_channels(self):
    return self.timing_channels

  @Pyro4.expose
  def get_routeable_backplane_signals(self):
    return self.signals

  @Pyro4.expose
  def set_device_config( self, config, channels, signal_graph ):
    # we need to separate channels first by device
    # (configs are already naturally separated by device)
    # in addition, we use collect_prefix to drop the 'vp/DevX' part of the
    # channel paths
    chans = collect_prefix(channels, 0, 2, 2)
    for d,dev in self.devices.items():
      if d in config or d in chans:
        dev.set_config( config.get(d,{}), chans.get(d,[]), signal_graph )

  @Pyro4.expose
  def set_clocks( self, clocks ):
    clocks = collect_prefix(clocks, 0, 2)
    for d,dev in self.devices.items():
      if d in clocks:
        dev.set_clocks( clocks[d] )

  @Pyro4.expose
  def set_signals( self, signals ):
    signals = collect_prefix(signals, 0, 2, prefix_list=self.devices)
    for d,dev in self.devices.items():
      dev.set_signals( signals.get(d,{}) )

  @Pyro4.expose
  def set_static(self, analog, digital):
    assert len(analog) == 0, 'Viewpoint does not perform analog output'
    D = collect_prefix(digital, 0, 2, 2)
    for dev in D.items():
      self.devices[ dev[0] ].set_output( dev[1] )

  @Pyro4.expose
  def set_waveforms(self, analog, digital, transitions, t_max, continuous):
    """
    Set the waveform for the viewpoint driver.
    """
    assert len(analog) == 0, 'Viewpoint does not perform analog output'
    D = collect_prefix(digital, 0, 2, 2)
    C = collect_prefix(transitions, 0, 2, 2)
    for d,dev in self.devices.items():
      if d in D or d in C:
        dev.set_waveforms( D.get(d,{}), C.get(d,{}), t_max, continuous )
