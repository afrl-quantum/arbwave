# vim: ts=2:sw=2:tw=80:nowrap

from physical import unit

class Base(object):
  """Base channel class"""
  _pyro_ = True # For remote connections, this class must use pyro
  _padded_timing   = True
  _finite_end_clock = False

  def __init__(self, name, dev=None):
    super(Base,self).__init__()
    self.name = name
    self.dev = dev

  def __str__(self):
    return self.name

  def get_config_template(self):
    return dict()

  @property
  def prefix(self):
    return self.name.partition('/')[0]

  @property
  def device(self):
    return self.dev

  def padded_timing(self):
    """
    Identifies a channel that simply writes an output value for every clock.
    This type requires padding, for when a clock must occur but an output is not
    requested to change.  This is typical for hardware like NI hardware that
    uses a simple FIFO style buffer for generating output on every clock.
    """
    return self._padded_timing

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.
    """
    return 0*unit.s

  def finite_mode_requires_end_clock(self):
    return self._finite_end_clock

  def type(self):
    return self._type

  def fullname(self):
    # we capitalize the first letter!
    T = self.type()
    return '{}{}/{}'.format( T[0].upper(), T[1:], self.name )
