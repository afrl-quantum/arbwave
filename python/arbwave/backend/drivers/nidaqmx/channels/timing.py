# vim: ts=2:sw=2:tw=80:nowrap

import sys
from .....tools.float_range import float_range
from ....channels import Timing as TBase, RecursiveMinPeriod
from .base import Base

class Timing(Base, TBase):
  """NIDAQmx Timing channel class"""
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


class DOTiming(Base, TBase):
  """Digital-output NIDAQmx Timing channel class"""
  aperiodic = True # digital line can generate an asynchronous signal.

  def _divider(self):
    return self.device.clocks[ str(self) ]['divider']['value']

  def get_min_period(self):
    return RecursiveMinPeriod( self.device.config['clock']['value'],
                               self._divider() )

  def get_config_template(self):
    return {
      'divider' : {
        'value' : 2,
        'type'  : int,
        'range' : xrange(2, sys.maxint),
      }
    }



class SCTB_Timing(Base, TBase):
  """
  NIDAQmx Timing channel class for output channels timed from a division of the
  ?/SampleClockTimebase.
  """

  def _divider(self):
    return self.device.clocks[ str(self) ]['divider']['value']

  def get_min_period(self):
    """
    Return a multiplication of the ?/SampleClockTimebase.
    """
    return RecursiveMinPeriod( self.device.config['clock-settings']['Timebase']['clock']['value'],
                               self._divider() )

  def get_config_template(self):
    return {
      'divider' : {
        'value' : 2,
        'type'  : int,
        'range' : xrange(2, sys.maxint),
      }
    }
