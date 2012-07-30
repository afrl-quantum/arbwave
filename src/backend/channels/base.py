# vim: ts=2:sw=2:tw=80:nowrap

from physical import unit

class Base:
  """Base channel class"""
  def __init__(self, name, dev=None, explicit_timing=True, finite_end_clock=True):
    self.name = name
    self.dev = dev
    self._explicit_timing = explicit_timing
    self._finite_end_clock = finite_end_clock

  def __str__(self):
    return self.name

  def get_config_template(self):
    return dict()

  def prefix(self):
    return self.name.partition('/')[0]

  def device(self):
    return self.dev

  def explicit_timing(self):
    return self._explicit_timing

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    return 0*unit.s

  def finite_mode_requires_end_clock(self):
    return self._finite_end_clock
