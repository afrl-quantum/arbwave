# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated remote connections to AFRL/Beaglebone Black devices.
"""

from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog
import time
import Pyro4
from physical import units

from .device.controller.bbb_pyro import format_objectId
from .device.controller import dds_details
from .device.controller import timing_details
from .device.controller import analog_details
from ....version import version as arbwave_version
from ....tools.dict import Dict

ANALOG_RANGE = {
  '(0V, 5V)'     : Dict(val=0b000, min=0,    max=5),
  '(0V, 10V)'    : Dict(val=0b001, min=0,    max=5),
  '(-5V, 5V)'    : Dict(val=0b010, min=-5,   max=5),
  '(-10V, 10V)'  : Dict(val=0b011, min=-10,  max=10),
  '(-2.5V, 2.5V)': Dict(val=0b100, min=-2.5, max=2.5),
}

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
      format_objectId('bbb0','analog') : Analog,
      format_objectId('bbb1','analog') : Analog,
    }

  def list(self, prefix=None, regex=None, metadata_all=None, metadata_any=None,
           return_metadata=False):
    if not {regex,metadata_all,metadata_any}.issubset({None}) or \
       return_metadata != False:
      raise RuntimeError('bbb.sim.NS: other args not yet supported')

    return {
      obj : '{protocol}{obj}'.format(protocol=self.protocol, obj=obj)
      for obj in self.registry if obj.startswith(prefix if prefix else '')
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
    self._owner = None
    self._pyroAttrs = dir(self)

  def _pyroRelease(self):
    pass
  @property
  def owner(self):
    return self._owner
  @owner.setter
  def owner(self, value):
    self._owner = value
  def reset(self):
    pass
  def get_version(self):
    """return the Arbwave version"""
    return arbwave_version()
  def set_output(self, values):
    pass
  def exec_waveform(self, n):
    self.n = n
    pass
  def waitfor_waveform(self, timeout):
    # wait for t_max amount of time (specified in milliseconds as per afrl-bbb)
    time.sleep(0.5 * timeout * 0.001)
    n = self.n
    self.n = None
    return n
  def stop(self):
    pass
  def flush_input(self):
    pass


class DDS(Device, dds_details.Details):
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

  def load_waveform(self, W):
    pass


class Timing(Device, timing_details.Details):
  type = 'timing'
  data = 0
  triggered = False
  retrigger = False
  trigger_level = 'low'
  trigger_pull = 'down'
  start_delay = 3
  minimum_period = 15
  waveform = list()

  def set_waveform_size(self, sz):
    self.waveform = [Dict() for i in range(sz)]

  set_output = timing_details.Details.set_output


class Analog(Device, analog_details.Details):
  type = 'analog'
  max_channels = 16
  single_overhead = 10
  per_channel_cost = 117
  update_src = 'timing/0'
  monitor = Dict(channel=0, enable=False)
  enable_external_reference = False
  disable_thermal_protection = False

  toggle_state = False
  toggle_channels = 0 # bit-array

  def __init__(self, *a, **kw):
    super(Analog, self).__init__(*a, **kw)
    self.spans = ['(0V, 5V)' for i in range(self.max_channels)]

  def get_minimum_period(self, n_chans):
    if n_chans > self.max_channels:
      raise RuntimeError('bbb:Analog:  more channels requested than available')
    return self.single_overhead + n_chans * self.per_channel_cost

  def get_monitor(self):
    return self.monitor

  def set_monitor(self, channel, enable):
    if not ( 0 <= channel < 16):
      raise RuntimeError('bbb.analog.set_monitor: invalid channel')
    self.monitor = Dict(channel=channel, enable=enable)

  def get_chip_config(self):
    return Dict(
      enable_external_reference = False,
      disable_thermal_protection = False,
    )

  def set_chip_config(self, disable_thermal_protection):
    self.disable_thermal_protection = disable_thermal_protection

  def get_toggle_select(self):
    return self.toggle_channels

  def set_toggle_select(self, channels):
    self.toggle_channels = channels

  def get_toggled(self):
    return self.toggle_state

  def set_toggled(self, toggled):
    self.toggle_state = toggled

  def get_span_values(self):
    return list(ANALOG_RANGE.keys())

  def get_span(self, channel):
    return self.spans[channel]

  def set_span(self, span, channel=None, all=False):
    assert span in ANALOG_RANGE, 'bbb.analog.set_span: invalid span'

    if all:
      for ch in range(self.max_channels):
        self.spans[ch] = span
    elif channel is None:
      raise RuntimeError('bbb.analog: must specify all=True or channel=<num> '
                         'for setting channel span')
    else:
      self.spans[channel] = span

  def volts_to_DAC(self, channel, data):
    rng = ANALOG_RANGE[self.get_span(channel)]
    maxdata = (1 << 16) - 1
    return int(
      min(max((data - rng.min) * (maxdata / (rng.max - rng.min)), 0), maxdata)
    )

  def load_waveform(self, wlen, channel_bits, flat_waveform):
    debug('%s.set_waveform_length(%d, %s)', self.objectId,
          wlen, bin(channel_bits))
    debug('%s.waveform[:] = <...>', self.objectId)
    for val in flat_waveform:
      if type(val) is not int:
        raise RuntimeError(
          'bbb.analog.load_waveform: Waveform components must be integers')

  base_set_output = Device.set_output
  set_output = analog_details.Details.set_output
