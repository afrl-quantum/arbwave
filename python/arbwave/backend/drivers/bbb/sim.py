# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated remote connections to AFRL/Beaglebone Black devices.
"""

from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog
import time
import Pyro4
from physical import units

from .device.controller.bbb_pyro import format_objectId
from ....version import version as arbwave_version

class NS(object):
  """
  Simulated Pyro name server and connection interface.
  """
  protocol = 'PYROSIM://'

  def __init__(self):
    self.registry = {
      format_objectId('bbb0','dds')    : DDS,
      format_objectId('bbb1','dds')    : DDS,
      format_objectId('bbb0','timing') : Timing,
      format_objectId('bbb1','timing') : Timing,
    }

  def list(self, prefix=None, regex=None, metadata_all=None, metadata_any=None,
           return_metadata=False):
    if not {regex,metadata_all,metadata_any}.issubset({None}) or \
       return_metadata != False:
      raise RuntimeError('bbb.sim.NS: other args not yet supported')

    return {
      obj : '{protocol}{obj}'.format(protocol=self.protocol, obj=obj)
      for obj in self.registry if obj.startswith(prefix + '.')
    }

  def Proxy(self, uri):
    _, protocol, oid = uri.partition(self.protocol)
    if _ != '' or protocol != self.protocol:
      raise Pyro4.errors.ProtocolError('unsupported protocol')
    if oid not in self.registry:
      raise Pyro4.errors.ProtocolError('connection failed')

    hostid = oid.partition('.')[-1].split('/')[0]
    return self.registry[oid](uri, hostid)


class Device(object):
  def __init__(self, uri, hostid):
    super(Device,self).__init__()
    self.hostid = hostid
    self.objectId = format_objectId(hostid, self.type)
    self.URI = uri
    self.n = None

  def _pyroRelease(self):
    pass
  def get_version(self):
    """return the Arbwave version"""
    return arbwave_version()
  def set_output(self, values):
    pass
  def set_waveforms(self, waveforms, clock_transitions, t_max):
    pass
  def exec_waveform(self, n):
    self.n = n
    pass
  def waitfor_waveform(self, timeout):
    time.sleep(0.5 * timeout) # wait for t_max amount of time
    n = self.n
    self.n = None
    return n
  def stop(self):
    pass


class DDS(Device):
  type = 'dds'
  sysclk = 500e6
  refclk = 10e6
  charge_pump = '75uA'
  refclk_src = 'tcxo'
  update_src = 'timing/0'

  CHARGE_PUMP_VALUES = [
    '75uA',
    '100uA',
    '125uA',
    '150uA',
  ]


  def set_sysclk_float(self, refclk, sysclk, charge_pump):
    debug('bbb(%s).set_sysclk_float(%s, %s, %s)',
          self.objectId, refclk, sysclk, charge_pump)
    self.sysclk = sysclk
    self.refclk = refclk
    self.charge_pump = charge_pump

  def get_sysclk_float(self):
    return dict(
      sysclk = self.sysclk,
      refclk = self.refclk,
      charge_pump = self.charge_pump,
    )

  def get_charge_pump_values(self):
    return self.CHARGE_PUMP_VALUES

  def set_frequency(self, f, chselect=1):
    pass
  def get_minimum_period(self, n_chans):
    # not correct, but gets close
    return dict(
      set_frequency          = ((304-82.5)*n_chans),
      set_frequency_sweep    = ((724-82.5)*n_chans),
      update_frequency_sweep = ((472-82.5)*n_chans),
    )
  def set_waveforms(self, waveforms, n_chans):
    pass


class Timing(Device):
  type = 'dds'
  data = 0
  triggered = False
  retrigger = False
  trigger_level = 'low'
  trigger_pull = 'down'
  start_delay = 3
