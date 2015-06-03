# vim: ts=2:sw=2:tw=80:nowrap

from .timing      import Timing
from ....channels import Analog as ABase
from ....channels import Digital as DBase
from ....channels import Backplane as BBase

class ComediChannel:
  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    return self.device.get_min_period()


class Analog(ComediChannel, ABase): pass
class Digital(ComediChannel, DBase): pass
class Backplane(BBase): pass

klasses = dict(
  to = Timing,
  ao = Analog,
  do = Digital,
  backplane = Backplane,
)
