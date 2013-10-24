# vim: ts=2:sw=2:tw=80:nowrap
"""
This package contains functions that can be used inside 'value' elements.

As an example, the Ramp class is used in a way to allow the user to specify
'ramp(10,.5)' to ramp from the current value to a value of 10 using an exponent
of 0.5 over the duration of the waveform element.
"""

from scipy.interpolate import interp1d
import numpy as np
import math
import physical
machine_arch = np.MachAr()
from logging import log, info, debug, warn, critical, DEBUG, root as rootlog

class step_iter:
  def __init__(self, ti, tf, dt, fun):
    self.t = ti
    self.tf = tf
    self.dt = dt
    self.fun = fun
  def __iter__(self):
    return self
  def next(self):
    if self.t >= self.tf:
      raise StopIteration()
    t = self.t

    self.t += self.dt
    v = self.fun(t)
    if self.t >= self.tf:
      # last one
      return t,       1, v
    else:
      return t, self.dt, v


###################


def getcoeff( val ):
  try: return val.coeff
  except: return val

def getunity( val ):
  try: return physical.Quantity(1,val.units)
  except: return 1.0


class SinPulse:
  """
  Generate a sinusoidal pulse over the duration of a waveform element.
  """
  name = 'sinpulse'
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
    self.dt_clk = None
    self.t = None
    self.duration = None

  def __repr__(self):
    return '{}({}, {}, {}, {}, {})' \
      .format(self.name, self.A, self.F, self.average, self.phase_shift,
              self.steps_per_cycle)

  def __call__(self, t):
    """
    Return the value of the sin pulse at relative time t.

    t_rel : relative time from beginning of sinpulse
    """
    t_rel = (t - self.t)
    if t_rel >= self.duration:
      return self.average

    t_rel *= self.dt_clk
    return self.average + self.A * math.sin(self.phase_shift + 2*np.pi * self.F * t_rel)


  def set_vars(self, _from, t, duration, dt_clk):
    """
      t and duration are integer time in units of dt_clk
    """
    if self.average is None:
      self.average = _from
    elif _from is not None \
         and getcoeff(abs(self.average - _from)) <= 10*machine_arch.eps:
      # the user specified the value that the channel is already at
      self.skip_first = True
    self.t = t
    self.dt_clk = dt_clk

    # it is important to make sure that the final value is given at
    # dt-self.dt_clk.  This allows for the following clock pulse to be used by
    # the next waveform element.
    self.duration = duration - 1
    self.dt = int(round( 1. / (self.F * self.steps_per_cycle) / dt_clk ))

    if self.dt > self.duration:
      raise RuntimeError( 'sinpulse:  requested stepsize too large' )
    if self.dt < 1:
      raise RuntimeError( 'sinpulse:  requested #steps too large' )

  def __iter__(self):
    # Note that the first data point (i.e. t=0) is implicitly given by _from
    # (where the channel is before this ramp).
    if self.skip_first:
      ti = self.t + self.dt
    else:
      ti = self.t
    return step_iter(ti, self.t+self.duration, self.dt, self)



###################


class Ramp:
  """
  Ramp from initial value to final value with a given exponent.
  """
  name = 'ramp'
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
    self.dt_input = dt
    self.dt = None
    self.t = None
    self.duration = None

  def __repr__(self):
    return '{}({}, {}, {}, {}, {})' \
      .format(self.name, self.to, self.exponent,
              self.steps, self._from, self.dt_input)

  def __call__(self, t):
    """
    Return the value of the ramp at normalized relative time t.

    t : normalized relative time, from 0.0 to 1.0
    """
    t_norm = (t - self.t) / float(self.duration)
    return self._from - t_norm**self.exponent * (self._from - self.to)

  def set_vars(self, _from, t, duration, dt_clk):
    """
      t and duration are integer time in units of dt_clk
    """
    if self._from is None:
      self._from = _from
    elif _from is not None \
         and getcoeff(abs(self._from - _from)) <= 10*machine_arch.eps:
      self.skip_first = True
    self.t = t

    # it is important to make sure that the final value is given at
    # dt-dt_clk.  This allows for the following clock pulse to be used by
    # the next waveform element.
    self.duration = duration - 1
    if self.dt_input:
      self.dt = int( round(self.dt_input/dt_clk) )
    else:
      self.dt = int(self.duration / self.steps)

    if self.dt > self.duration:
      raise RuntimeError( 'ramp:  requested stepsize too large' )
    if self.dt < 1:
      raise RuntimeError( 'ramp:  requested #steps too large' )


  def __iter__(self):
    # Note that the first data point (i.e. t=0) is implicitly given by _from
    # (where the channel is before this ramp).
    if self.skip_first:
      ti = self.t + self.dt
    else:
      ti = self.t
    return step_iter(ti, self.t+self.duration, self.dt, self)



class Pulse:
  """
  Generate a pulse over the duration of a waveform element.
  """
  name = 'pulse'
  def __init__(self, high=True,low=None):
    """
    Usage:  pulse(high=True, low=None)

    high  : The value to generate for the pulse.
    low   : The value to return to after the pulse.
            If low is not set (left as None) it will be set differently for
            analog and digital channels.  If the high is a boolean value, low
            will be set to its logical complement.  Otherwise, if low is not
            set, it will be set to whatever the channel is at prior to this
            pulse.
   """
    self.high     = high
    self.low      = low
    self._from    = None
    self.t        = None
    self.duration = None

  def __repr__(self):
    return '{}({}, {})'.format(self.name, self.high, self.low)

  def set_vars(self, _from, t, duration, dt_clk):
    """
      t and duration are integer time in units of dt_clk
    """
    self._from = _from
    if self.low is None:
      if type(self.high) is bool:
        self.low = not self.high
      else:
        self.low = _from
    self.t = t
    self.duration = duration - 1

  def __iter__(self):
    L = list()
    if self._from is None or self._from != self.high:
      # we only really need to add the transition to go high if the channel was
      # not already high
      L.append( (self.t, self.duration, self.high) )

    # add the transition to the low value
    # take care to avoid machine precision problems by moving the start time
    # ahead a tiny bit.
    L.append( (self.t + self.duration, 1, self.low) )
    return iter(L)

class PulseTrain:
  """
  Generate a train of pulses over the duration of a waveform element.
  """
  name = 'pulses'
  def __init__(self, n, duty=0.5, high=True, low=None, dt=None):
    """
    Usage:  pulses(n, duty=0.5, high=True, low=False, dt=None)

    n     : Number of evenly spaced pulses to generate.
    duty  : Duty cycle (only used if dt is not set) [Default 0.5].
    high  : The value to generate for each pulses [Default:  True].
    low   : The value to return to after the pulse.
            If low is not set (left as None) it will be set differently for
            analog and digital channels.  If the high is a boolean value, low
            will be set to its logical complement.  Otherwise, if low is not
            set, it will be set to whatever the channel is at prior to this
            pulse.
    dt    : On width of a single pulse in the pulse train
            [Default:  not set].
   """
    self.n        = n
    self.duty     = duty
    self.dt_on    = dt
    self.high     = high
    self.low      = low
    self._from    = None
    self.t        = None
    self.duration = None

  def __repr__(self):
    return '{}({}, {}, {}, {}, {})' \
      .format(self.name, self.n, self.duty, self.high, self.low, self.dt_on)

  def set_vars(self, _from, t, duration, dt_clk):
    """
      t and duration are integer time in units of dt_clk
    """
    self._from = _from
    if self.low is None:
      if type(self.high) is bool:
        self.low = not self.high
      else:
        self.low = _from
    self.t = t
    duration = duration - 1

    self.pulse_period = int(duration / self.n)
    max_dt_on = self.pulse_period - 1
    if self.dt_on is None:
      # use duty cycle by default
      if self.duty is None or self.duty < 0 or self.duty > 1:
        raise RuntimeError('pulses:  duty cycle _must_ be between 0 and 1')

      if self.duty == 0:
        self.dt_on = 1
      else:
        self.dt_on = int( round(max_dt_on * self.duty) )
    else:
      self.dt_on = int(round( self.dt_on / dt_clk ))
      if self.dt_on > max_dt_on:
        raise RuntimeError(
          'pulses:  cannot make pulse train where dt > duration/n-dt_clk'
        )
    self.dt_off = self.pulse_period - self.dt_on

  def __iter__(self):
    L = list()
    t = self.t
    for i in xrange(self.n):
      L.append( (t,               self.dt_on, self.high) )
      L.append( (t + self.dt_on, self.dt_off,  self.low) )
      t += self.pulse_period

    if self._from is not None and self._from == self.high:
      # we only really need to add the first transition to go high if the
      # channel was not already high
      L.pop(0)

    return iter(L)


class Interpolate:
  """
  Interpolate through values of a data table specified by x and y values.  x
  represents time and y is the value at a specific time.
  """
  name = 'interp'
  default_steps = 20
  def __init__(self, x, y, steps=None, dt=None):
    """
    Usage:  interp(x, y, steps=20, dt=None)

    x       : time in arbitrary units.  Time will be normalized to 0-1 where
              time=1 corresponds to the maximum value in x.
    y       : y values to use in interpolation
    steps   : number of steps to take (Default: 20)
    dt      : the timestep to increment (Default: duration/steps)

    Only one of dt or steps can be used.
   """
    self.interp = interp1d( (x - min(x)) / float(max(x) - min(x)), y )
    self.unity = getunity( y[0] )
    if steps > 0:
      self.steps = steps
    else:
      self.steps = Interpolate.default_steps
    self.skip_first = False
    self.dt_input = dt
    self.dt = None
    self.t = None
    self.duration = None
    self.tf_safe = None

  def __repr__(self):
    return '{}(<x>, <y>, {}, {})'.format(self.name, self.steps, self.dt_input)

  def __call__(self, t):
    """
    Return the value of the interpolator at normalized relative time t.

    t : normalized relative time, from 0.0 to 1.0
    """
    t_norm = (t - self.t) / float(self.duration)
    return self.interp( min(1.0, t_norm) ) * self.unity

  def set_vars(self, _from, t, duration, dt_clk):
    """
      t and duration are integer time in units of dt_clk
    """
    if _from is not None and \
      getcoeff(abs(self.interp(0.)*self.unity - _from)) <= 10*machine_arch.eps:
      self.skip_first = True
    self.t = t

    # it is important to make sure that the final value is given at
    # dt-self.dt_clk.  This allows for the following clock pulse to be used by
    # the next waveform element.
    self.duration = duration - 1
    if self.dt_input:
      self.dt = int( round(self.dt_input/dt_clk) )
    else:
      self.dt = int(self.duration / self.steps)

    if self.dt > self.duration:
      raise RuntimeError( 'interp:  requested stepsize too large' )
    if self.dt < 1:
      raise RuntimeError( 'interp:  requested #steps too large' )


  def __iter__(self):
    if self.skip_first:
      ti = self.t + self.dt
    else:
      ti = self.t
    return step_iter(ti, self.t+self.duration, self.dt, self)


registered = {
  SinPulse.name   : SinPulse,
  Ramp.name       : Ramp,
  Pulse.name      : Pulse,
  PulseTrain.name : PulseTrain,
  Interpolate.name: Interpolate,
}
