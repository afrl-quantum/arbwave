# vim: ts=2:sw=2:tw=80:nowrap

from physical import unit
from ....channels import Timing as Base

class Timing(Base):
  """DIO64 Timing channel class"""

  def get_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    print 'timing.get_period()...'
    return self.device().board.configs['out']['scan_rate']*unit.s
