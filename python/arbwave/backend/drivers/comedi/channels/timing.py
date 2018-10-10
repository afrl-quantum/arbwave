# vim: ts=2:sw=2:tw=80:nowrap

import Pyro4

from physical import unit

from .....tools.float_range import float_range
from ....channels import Timing as TBase, RecursiveMinPeriod
from .base import Base

__all__ = ['Timing', 'DOTiming', 'OnboardClock']

class Timing(Base, TBase):
  """Comedi Timing channel class"""
  @Pyro4.expose
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
  """Digital-output Comedi Timing channel class"""
  aperiodic = True # digital line can generate an asynchronous signal.

  def _divider(self):
    return self.device.clocks[ str(self) ]['divider']['value']

  @Pyro4.expose
  def get_min_period(self):
    return RecursiveMinPeriod( self.device.config['clock']['value'],
                               self._divider() )

  @Pyro4.expose
  def get_config_template(self):
    return {
      'divider' : {
        'value' : 2,
        'type'  : int,
        'range' : range(2, sys.maxsize),
      }
    }


class OnboardClock(Base, TBase):
  """
  Comedi Timing channel class for onboard output timer.  For example, the NI/AO
  subdevices generally all have their own onboard output timer.
  """

  @Pyro4.expose
  def get_min_period(self):
    OC = self.device.onboardclock_name
    return unit.s / self.device.clocks[OC]['rate']['value']

  @Pyro4.expose
  def get_config_template(self):
    return {
      'rate' : {
        'value' : 1000,
        'type'  : float,
        # FIXME:  find a way of knowing/determining the maximum rate for a
        # particular device.  For right now, I'm selecting the maximum I know
        # (which is for the PCI-6534 device).
        'range' : float_range(0.0,20e6, include_beginning=False),
      }
    }
