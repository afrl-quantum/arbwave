# vim: ts=2:sw=2:tw=80:nowrap
"""
This package contains functions that can be used inside 'value' elements.

As an example, the Ramp class is used in a way to allow the user to specify
'ramp(10,.5)' to ramp from the current value to a value of 10 using an exponent
of 0.5 over the duration of the waveform element.
"""

import numpy as np
machine_arch = np.MachAr()

class step_iter:
  def __init__(self, ti, tf, dt, min_period, fun):
    self.t = ti
    self.tf = tf
    self.dt = dt
    self.min_period = min_period
    self.fun = fun
  def __iter__(self):
    return self
  def next(self):
    if self.t >= self.tf:
      raise StopIteration()
    t = self.t

    self.t += self.dt
    if self.t >= self.tf:
      # last one
      return t, self.min_period, self.fun(t)
    else:
      return t, self.dt, self.fun(t)

class Ramp:
  """
  Ramp from initial value to final value with a given exponent.
  """
  default_steps = 20
  def __init__(self, to, exponent=1.0, steps=None, _from=None,dt=None):
    """
    Usage:  ramp(to, exponent=1.0, steps=10, _from=None, dt=None)

    to      : final value to which to ramp
    _from   : initial value from which to ramp
    exponent: exponent with which to ramp
    dt      : the timestep to increment (Default: duration/steps)
    steps   : number of steps to take

    Only one of dt or steps can be used.
   """
    self.to = to
    self.exponent = exponent
    if steps:
      self.steps = steps
    else:
      self.steps = Ramp.default_steps
    self._from = _from
    self.skip_first = _from is None
    self.dt = dt
    self.t = None
    self.duration = None
    self.tf_safe = None

  def __call__(self, t):
    """
    Return the value of the ramp at normalized relative time t.

    t : normalized relative time, from 0.0 to 1.0
    """
    t_norm = (t - self.t) / self.duration
    return self._from - t_norm**self.exponent * (self._from - self.to)

  def set_vars(self, _from, t, duration, clock_period, min_transition_period):
    if self._from is None:
      self._from = _from
    elif abs(self._from - _from).coeff <= 10*machine_arch.eps:
      self.skip_first = True
    self.t = t
    # the "+ .4*clock_period" is to ensure that the min_period is rounded to
    # nearest clock_period such that the ramp ends at least max(clock_period,
    # min_transition_period) away from the next clock that is supposed to be
    # available for other waveforms.
    self.min_period = max(clock_period, min_transition_period) + .4*clock_period

    # it is important to make sure that the final value is given at
    # dt-self.min_period.  This allows for the following clock pulse to be used by
    # the next waveform element.
    self.duration = duration - self.min_period
    if not self.dt:
      self.dt = self.duration / float(self.steps)

    # tf safe is the comparison that is used to tell whether time-stepping
    # should cease.  We add one half a clock_period to avoid precision
    # error-prone comparisons.
    self.tf_safe = self.t+self.duration + 0.5*clock_period

  def __iter__(self):
    # Note that the first data point (i.e. t=0) is implicitly given by _from
    # (where the channel is before this ramp).
    if self.skip_first:
      ti = self.t + self.dt
    else:
      ti = self.t
    return step_iter(ti, self.tf_safe, self.dt, self.min_period, self)

class Pulse:
  """
  Generate a pulse over the duration of a waveform element.
  """
  def __init__(self, high=True,low=False):
    """
    Usage:  pulse(high=True, low=False)

    high  : The value to generate for the pulse.
    low   : The value to return to after the pulse
   """
    self.high = high
    self.low = low
    self._from = None
    self.t = None
    self.duration = None
    self.min_period = None

  def set_vars(self, _from, t, duration, clock_period, min_transition_period):
    self._from = _from
    self.t = t
    # the "+ .4*clock_period" is to ensure that the min_period is rounded to
    # nearest clock_period such that the ramp ends at least max(clock_period,
    # min_transition_period) away from the next clock that is supposed to be
    # available for other waveforms.
    self.min_period = max(clock_period, min_transition_period) + .4*clock_period
    self.duration = duration - self.min_period

  def __iter__(self):
    L = list()
    if self._from is None or self._from != self.high:
      # we only really need to add the transition to go high if the channel was
      # not already high
      L.append( (self.t, self.duration, self.high) )

    # add the transition to the low value
    L.append( (self.t + self.duration, self.min_period, self.low) )
    return iter(L)

registered = {
  'ramp'  : Ramp,
  'pulse' : Pulse,
}
