# vim: ts=2:sw=2:tw=80:nowrap
"""
This package contains functions that can be used inside 'value' elements.

As an example, the Ramp class is used in a way to allow the user to specify
'ramp(10,.5)' to ramp from the current value to a value of 10 using an exponent
of 0.5 over the duration of the waveform element.
"""

class Ramp:
  """
  Ramp from initial value to final value with a given exponent.
  """
  def __init__(self, Vi, dt):
    """
    Vi  : initial value from which to ramp
    dt  : normalized time step, where t=1 is the end of the current waveform
          element.
          Note that the first data point (i.e. t=0) is implicitly given by the
          value Vi.
   """
    self.Vi = Vi
    self.dt = dt
    self.t = 0.0
  def __call__(self, to, exponent, _from=None ):
    if not _from:
      _from = self.Vi
    return _from - (self.t+self.dt)**exponent * (_from - to), 1.0

registered = {
  'ramp' : Ramp,
}

def get(Vi,dt):
  """
  Get all functions for initial value Vi and time step dt.

  This function is used to return a dictionary of functions to be added to
  locals while evaluating values.
  """
  retval = dict()
  for f in registered:
    retval[f] = registered[f](Vi,dt)
  return retval
