# vim: ts=2:sw=2:tw=80:nowrap

from base import Base

class Timing(Base):
  """Base Timing channel class"""

  def is_aperiodic(self):
    """
    Returns whether this clock represents an aperiodic signal.
    """
    return False
