# vim: ts=2:sw=2:tw=80:nowrap

from .....tools.float_range import float_range
from ....channels import Timing as Base

class Timing(Base):
  """Base NIDAQmx Timing channel class"""
  def get_config_template(self):
    return {
      'idle-state' : {
        'value' : 'low',
        'type'  : str,
        'range' : ['low', 'high'],
      },
      'delay' : {
        'value' : 0.0,
        'type'  : float,
        'range' : float_range(0.0,0.0, include_end=True),
      },
      'rate' : {
        'value' : 1.0,
        'type'  : float,
        'range' : float_range(1.0,40e6, include_end=True),
      },
      'duty-cycle' : {
        'value' : 0.5,
        'type'  : float,
        'range' : float_range(0.0,1.0, include_beginning=False),
      },
    }
