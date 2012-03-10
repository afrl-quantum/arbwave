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
  def __init__(self, Vi, t):
    """
    Vi  : initial value from which to ramp
    t   : normalized time, where t=1 is the end of the current waveform element.
    """
    self.Vi = Vi
    self.t = t
  def __call__(self, Vf, exponent):
    return self.Vi - self.t**exponent * (self.Vi - Vf)

registered = {
  'ramp' : Ramp,
}

def get(Vi,t):
  """
  Get all functions for initial value Vi and time t.

  This function is used to return a dictionary of functions to be added to
  locals while evaluating values.
  """
  retval = dict()
  for f in registered:
    retval[f] = registered[f](Vi,t)
  return retval
