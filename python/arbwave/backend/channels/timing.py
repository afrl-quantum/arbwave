# vim: ts=2:sw=2:tw=80:nowrap

import Pyro4

from .base import Base

class Timing(Base):
  """Base Timing channel class"""
  _type = 'timing'
  aperiodic = False

  @Pyro4.expose
  @property
  def is_aperiodic(self):
    """
    Returns whether this clock represents an aperiodic signal.
    """
    return self.aperiodic



class RecursiveMinPeriod(object):
  """
  Optional return value for Timing.get_min_period, such that a clock can
  indicate its dependence on another clock.  This allows for waveforms to be
  calculated correctly regardless whether devices use independent or dependent
  clocks.
  """
  def __init__(self, parent_clock, scaling):
    # a device can use this to have arbwave compute engine always figure out the
    # proper dependence.  A driver can also optionally check to see if it
    # actually owns the clock and calculate its min_period if possible at the
    # driver level.
    self.parent_clock = parent_clock # label of parent clock
    self.scaling = scaling
    super(RecursiveMinPeriod,self).__init__()

  def __call__(self, parent_clock_min_period):
    return parent_clock_min_period * self.scaling

  def __str__(self):
    return '{} * {}'.format(self.parent_clock, self.scaling)
