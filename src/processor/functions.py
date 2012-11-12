# vim: ts=2:sw=2:tw=80:nowrap
"""
This package contains functions that can be used inside 'value' elements.

As an example, the Ramp class is used in a way to allow the user to specify
'ramp(10,.5)' to ramp from the current value to a value of 10 using an exponent
of 0.5 over the duration of the waveform element.
"""

import numpy as np
import math
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


###################



class SinPulse:
  """
  Generate a sinusoidal pulse over the duration of a waveform element.
  """
  default_steps_per_cycle = 20
  def __init__(self, A, F, average=None, phase_shift=0., steps_per_cycle=None):
    """
    Usage:  sinpulse(A, F, average=0., phase_shift=0., steps_per_cycle=None):

    A       : Amplitude (0-to-peak)
    F       : Frequency in Hz
    average : Average value of sine wave.
    phase_shift : 0 to 2 pi shift, where pi/2 represents +cos
    steps_per_cycle   : number of steps per cycle

    Only one of dt or steps can be used.
   """
    self.F = F
    self.A = A
    self.average = average
    self.phase_shift = phase_shift
    if steps_per_cycle > 0:
      self.steps_per_cycle = steps_per_cycle
    else:
      self.steps_per_cycle = self.default_steps_per_cycle
    self.skip_first = average is None
    self.dt = None
    self.t = None
    self.duration = None
    self.tf_safe = None

  def __call__(self, t):
    """
    Return the value of the sin pulse at relative time t.

    t_rel : relative time from beginning of sinpulse
    """
    if t > (self.tf_safe - self.dt):
      return self.average

    t_rel = (t - self.t)
    return self.average + self.A * math.sin(self.phase_shift + 2*np.pi * self.F * t_rel)


  def set_vars(self, _from, t, duration, min_period):
    if self.average is None:
      self.average = _from
    elif _from is not None \
         and abs(self.average - _from).coeff <= 10*machine_arch.eps:
      # the user specified the value that the channel is already at
      self.skip_first = True
    self.t = t
    self.min_period = min_period

    # it is important to make sure that the final value is given at
    # dt-self.min_period.  This allows for the following clock pulse to be used by
    # the next waveform element.
    self.duration = duration - self.min_period
    self.dt = 1. / (self.F * self.steps_per_cycle)
    # tf safe is the comparison that is used to tell whether time-stepping
    # should cease.  We add one half a min_period to avoid precision
    # error-prone comparisons.
    self.tf_safe = self.t+self.duration + 0.5*min_period

  def __iter__(self):
    # Note that the first data point (i.e. t=0) is implicitly given by _from
    # (where the channel is before this ramp).
    if self.skip_first:
      ti = self.t + self.dt
    else:
      ti = self.t
    return step_iter(ti, self.tf_safe, self.dt, self.min_period, self)



###################


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
    if steps > 0:
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

  def set_vars(self, _from, t, duration, min_period):
    if self._from is None:
      self._from = _from
    elif _from is not None \
         and abs(self._from - _from).coeff <= 10*machine_arch.eps:
      self.skip_first = True
    self.t = t
    self.min_period = min_period

    # it is important to make sure that the final value is given at
    # dt-self.min_period.  This allows for the following clock pulse to be used by
    # the next waveform element.
    self.duration = duration - self.min_period
    if not self.dt:
      self.dt = self.duration / float(self.steps)

    # tf safe is the comparison that is used to tell whether time-stepping
    # should cease.  We add one half a min_period to avoid precision
    # error-prone comparisons.
    self.tf_safe = self.t+self.duration + 0.5*min_period

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

  def set_vars(self, _from, t, duration, min_period):
    self._from = _from
    self.t = t
    self.min_period = min_period
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

class PulseTrain:
  """
  Generate a pulse over the duration of a waveform element.
  """
  def __init__(self, n, duty=0.5, high=True,low=False, dt=None):
    """
    Usage:  pulse(n, duty=0.5, high=True, low=False, dt=None)

    n     : Number of evenly spaced pulses to generate.
    duty  : Duty cycle (only used if dt is not set) [Default 0.5].
    high  : The value to generate for the pulse [Default:  True].
    low   : The value to return to after the pulse [Default:  False].
    dt    : On width of a single pulse in the pulse train
            [Default:  not set].
   """
    self.n          = n
    self.duty       = duty
    self.dt_on      = dt
    self.high       = high
    self.low        = low
    self._from      = None
    self.t          = None
    self.duration   = None
    self.min_period = None

  def set_vars(self, _from, t, duration, min_period):
    self._from = _from
    self.t = t
    self.min_period = min_period
    self.duration = duration - self.min_period

    self.pulse_period = duration / self.n
    max_dt_on = self.pulse_period - min_period
    if self.dt_on is None:
      # use duty cycle by default
      if self.duty is None or self.duty < 0 or self.duty > 1:
        raise RuntimeError('pulses:  duty cycle _must_ be between 0 and 1')

      if self.duty == 0:
        self.dt_on = min_period
      else:
        self.dt_on = max_dt_on * self.duty
    elif self.dt_on > max_dt_on:
      raise RuntimeError(
        'pulses:  cannot make pulse train where dt > duration/n-dt_clk'
      )
    self.dt_off = self.pulse_period - self.dt_on

  def __iter__(self):
    L = list()
    t = self.t
    for i in xrange(self.n):
      L.append( (t, self.dt_on, self.high) )
      L.append( (t + self.dt_on, self.dt_off, self.low) )
      t += self.pulse_period

    if self._from is not None and self._from == self.high:
      # we only really need to add the first transition to go high if the
      # channel was not already high
      L.pop(0)

    return iter(L)

registered = {
  'sinpulse' : SinPulse,
  'ramp'    : Ramp,
  'pulse'   : Pulse,
  'pulses'  : PulseTrain,
}
