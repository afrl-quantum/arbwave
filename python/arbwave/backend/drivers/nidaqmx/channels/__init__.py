# vim: ts=2:sw=2:tw=80:nowrap

from timing import Timing
from ....channels import Analog as ABase
from ....channels import Digital as DBase
from ....channels import Backplane

class NIChannel:
  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    return self.device.get_min_period()


class Analog(NIChannel, ABase):
  pass

class Digital(NIChannel, DBase):
  pass
