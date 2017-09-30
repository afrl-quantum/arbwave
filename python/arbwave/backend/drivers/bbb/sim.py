# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated remote connections to AFRL/Beaglebone Black devices.
"""

from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog
import time
import Pyro.core

from .device.controller.bbb_pyro import format_objectId
from ....version import version as arbwave_version

class NS(object):
  """
  Simulated Pyro name server and connection interface.
  """
  protocol = 'PYROSIM://'

  def __init__(self):
    self.registry = {
      ':bbb.bbb0/dds'     : DDS,
      ':bbb.bbb1/dds'     : DDS,
      ':bbb.bbb0/timing'  : Timing,
      ':bbb.bbb1/timing'  : Timing,
    }

  def list(self, pyro_group):
    return [
      (r.partition('.')[2], 1)
      for r in self.registry if r.startswith(pyro_group)
    ]

  def resolve(self, objectId):
    if objectId in self.registry:
      return self.protocol + objectId
    else:
      raise Pyro.core.NamingError('name not found', objectId)

  def getProxyForURI(self, uri):
    _, protocol, oid = uri.partition(self.protocol)
    if _ != '' or protocol != self.protocol:
      raise Pyro.core.ProtocolError('unsupported protocol')
    if oid not in self.registry:
      raise Pyro.core.ProtocolError('connection failed')

    hostid = oid.partition('.')[-1].split('/')[0]
    return self.registry[oid](uri, hostid)


class Device(object):
  def __init__(self, uri, hostid):
    super(Device,self).__init__()
    self.hostid = hostid
    self.objectId = format_objectId(hostid, self.type)
    self.URI = uri
    self.n = None

  def _release(self):
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
  def waitfor_waveform(self):
    time.sleep(.25) # wait an arbitrary time
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


  def set_sysclk(self, refclk, sysclk, charge_pump):
    debug('bbb(%s).set_sysclk(%s, %s, %s)',
          self.objectId, refclk, sysclk, charge_pump)
    self.sysclk = sysclk
    self.refclk = refclk
    self.charge_pump = charge_pump

  def get_sysclk(self):
    return dict(
      sysclk = self.sysclk,
      refclk = self.refclk,
      charge_pump = self.charge_pump,
    )

  def get_charge_pump_values(self):
    return self.CHARGE_PUMP_VALUES

  def set_frequency(self, f, chselect=1):
    pass


class Timing(Device):
  type = 'dds'
  data = 0
  triggered = False
  retrigger = False
  start_delay = 3
