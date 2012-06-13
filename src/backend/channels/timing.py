# vim: ts=2:sw=2:tw=80:nowrap

from physical import unit
from base import Base

class Timing(Base):
  """Base Timing channel class"""

  def is_aperiodic(self):
    """
    Returns whether this clock represents an aperiodic signal.
    """
    return False

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    return 0*unit.s
