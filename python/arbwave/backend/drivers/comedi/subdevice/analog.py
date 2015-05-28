# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
from .....tools.float_range import float_range
from subdevice import Subdevice as Base
import nidaqmx

class Analog(Base):
  subdev_type = 'ao'


  def add_channels(self):
    # populate the task with output channels and accumulate the data
    dflt_mn = self.config['default-voltage-range']['minimum']['value']
    dflt_mx = self.config['default-voltage-range']['maximum']['value']
    chans = self.channels.items()
    chans.sort( key = lambda v : v[1]['order'] )
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
