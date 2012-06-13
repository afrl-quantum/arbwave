# vim: ts=2:sw=2:tw=80:nowrap

from physical import unit
from ....channels import Timing as Base

class Timing(Base):
  """DIO64 Timing channel class"""

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
    return unit.s / self.device().board.configs['out']['scan_rate']
