# vim: ts=2:sw=2:tw=80:nowrap

from ....tools.float_range import float_range
from ...channels import Timing as TBase, Backplane

class Timing(TBase):
  """NIDAQmx Timing channel class"""
  def get_min_period(self):
    return 1. /self.dev.clocks[self.name]['rate']['value']

  def get_config_template(self):
    return {
      'rate' : {
        'value' : 1e7,
        'type'  : float,
        'range' : float_range(1.0,100e6, include_end=True),
      },
    }
