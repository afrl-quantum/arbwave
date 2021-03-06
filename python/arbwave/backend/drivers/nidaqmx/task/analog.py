# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
import Pyro4

from .....tools.float_range import float_range
from .task import Task as Base
from physical import unit
import nidaqmx

class Analog(Base):
  task_type = 'ao'
  task_class = nidaqmx.AnalogOutputTask

  # Refer to the NI documentation, DAQ-STC, Section 3.4.5.1 "Single-Buffer Mode"
  finite_end_clock = True


  def add_channels(self):
    # populate the task with output channels and accumulate the data
    dflt_mn = self.config['default-voltage-range']['minimum']['value']
    dflt_mx = self.config['default-voltage-range']['maximum']['value']
    chans = sorted(self.channels.items(), key = lambda v : v[1]['order'])
    for c in chans:
      if c[1]:
        mn, mx = c[1]['min'], c[1]['max']
      else:
        # use the default range values
        mn, mx = dflt_mn, dflt_mx
      debug( 'nidaqmx: creating analog output NIDAQmx channel: %s', c[0] )
      self.task.create_voltage_channel(
        c[0].partition('/')[-1], # cut off the prefix
        min_val=mn, max_val=mx )


  def get_min_period(self):
    if self.task and self.channels:
      # this is kind of hackish and might be wrong for other hardware (that is
      # not the PCI-6723).  The PCI-6723 did not like having < 1*..., therefore
      # we use max(1, .6*...).
      return max( 1, .6*len(self.channels) ) \
            * unit.s / self.task.get_sample_clock_max_rate()
    return 0*unit.s

  @Pyro4.expose
  def get_config_template(self):
    template = Base.get_config_template(self)
    template['default-voltage-range'] = {
      'minimum' : {
        'value' : -10.0,
        'type'  : float,
        'range' : float_range(-10.0, 10.0),
      },
      'maximum' : {
        'value' : 10.0,
        'type'  : float,
        'range' : float_range(-10.0, 10.0),
      },
    }
    return template
