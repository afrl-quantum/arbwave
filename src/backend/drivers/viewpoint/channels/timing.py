# vim: ts=2:sw=2:tw=80:nowrap

from physical import unit
from .....tools.float_range import float_range
from ....channels import Timing as Base

class Timing(Base):
  """DIO64 aperiodic/arbitrary timing channel class"""

  def is_aperiodic(self):
    """
    Returns whether this clock represents an aperiodic signal.
    """
    return True

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    # The factor of two is because scan_rate is the max transition rate of the
    # DIO64 output channels.  A device using this channel as an aperiodic clock
    # will need to see a rising edge and falling edge, the pair of which
    # constitutes one clock pulse.
    return 2 * unit.s / self.device().board.configs['out']['scan_rate']


class InternalTiming(Base):
  """DIO64 internal clock timing channel class"""

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    return unit.s / self.device().board.configs['out']['scan_rate']

  def get_config_template(self):
    # The limits on the scan_rate range are according to the manual...
    if str(self).endswith('_OCXO'): #oven-controlled crystal oscillator
      return {
        'scan_rate' : {
          'value' : 10e6,
          'type'  : float,
          'range' : float_range(0.0, 16e6),
        }
      }
    else: # or a normal crystal oscillator
      return {
        'scan_rate' : {
          'value' : 20e6,
          'type'  : float,
          'range' : float_range(0.0, 20e6),
        }
      }
