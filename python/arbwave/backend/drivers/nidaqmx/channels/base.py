# vim: ts=2:sw=2:tw=80:nowrap

from ....channels import Base as root_base

class Base(root_base):
  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    return self.device.get_min_period()
