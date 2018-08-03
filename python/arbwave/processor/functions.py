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
from physical import unit
from physical.sympy_util import has_sympy

machine_arch = np.MachAr()
from logging import log, info, debug, warn, critical, DEBUG, root as rootlog

from ..tools.dict import Dict

class step_iter:
  def __init__(self, ti, tf, dt, fun):
    self.t = ti
    self.tf = tf
    self.tf_m1 = tf - dt # time after last full step
    self.tf_stop = tf + 0.5*dt
    self.dt = dt
    self.fun = fun
  def __iter__(self):
    return self
  def __next__(self):
    if self.t >= self.tf_stop:
      raise StopIteration()

    if self.t >= self.tf:
      # last step of dt=1 before clock pulse of next waveform element
      self.t += self.dt # move the time beyond tf_stop
      return self.tf, 1, self.fun(self.tf)

    t = self.t
    if t >= self.tf_m1:
      # second to last one, finishing last full step
      self.t = self.tf
      return t, self.tf - t, self.fun(t)

    self.t += self.dt
    return t, self.dt, self.fun(t)


###################
class ScaledFunction(object):
  """
  Interface to change how the value-generator is presented when the eval_cache
  is shown to the user.
  """
  def __init__(self):
    super(ScaledFunction, self).__init__()
    self.units = None
    self.units_str = None
  def set_units(self, units, units_str):
    """
    Arbwave calls this function if it exists to give the generator the
    user-specified units and units string for the particular channel.
    """
    self.units = units
    self.units_str = units_str
  def ufmt(self, value):
    try:
      if self.units and self.units_str:
        return '{}*{}'.format(value / self.units, self.units_str)
    except: pass
    return value


def getcoeff( val ):
  try: return val.coeff
  except: return val

def getunity( val ):
  try: return physical.Quantity(1,val.units)
  except: return 1.0


class SinPulse(ScaledFunction):
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
    super(SinPulse, self).__init__()
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

  def get_encoding(self, capabilities):
    return 'linear' if 'linear' in capabilities else 'step'

  def __repr__(self):
    return '{}({}, {}*Hz, {}, {}, {})' \
      .format(self.name, self.ufmt(self.A), self.F/unit.Hz, self.ufmt(self.average),
              self.phase_shift, self.steps_per_cycle)

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


class Ramp(ScaledFunction):
  """
  Ramp from initial value to final value with a given exponent.
  """
  name = 'ramp'
  default_steps = 20
  def __init__(self, to, exponent=1.0, steps=None, _from=None,
               dt=None, duration=None):
    """
    Usage:  ramp(to, exponent=1.0, steps=20, _from=None, dt=None, duration=None)

    to      : final value to which to ramp
    _from   : initial value from which to ramp
    exponent: exponent with which to ramp
    steps   : number of steps to take
    dt      : the timestep to increment (Default: duration/steps)
    duration: Duration of ramp function.  Note that this is not necessarily
              equal to the actual duration of the steps generated by the ramp,
              since those are set in the "Duration" field of the waveform
              editor.  Value of None indicates that the ramp should last for the
              time specified in the "Duration" field of the waveform editor.
              [Default: None]

    Only one of dt or steps can be used.
    """
    super(Ramp, self).__init__()
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
    self.tf = duration # final time of ramp functional form (in seconds)
    self.tf_clk = None # final time of ramp functional form in dt_clk units

  def get_encoding(self, capabilities):
    return 'linear' if 'linear' in capabilities else 'step'

  def __repr__(self):
    tf = None if self.tf is None else self.tf/unit.s
    return '{}({}, {}, {}, {}, {}, {}*s)' \
      .format(self.name, self.ufmt(self.to), self.exponent,
              self.steps, self.ufmt(self._from), self.dt_input, tf)

  def __call__(self, t):
    """
    Return the value of the ramp at normalized relative time t.

    t : normalized relative time, from 0.0 to 1.0
    """
    t_norm = (t - self.t) / float(self.tf_clk)
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
    # t + (dt-dt_clk).  This allows for the clock pulse at (t+dt) to be used by
    # the next waveform element.
    self.duration = duration - 1

    # store the final time of the ramp functional
    # self.tf:  only used for repr(ramp(...)) for a visual to user (in seconds)
    # self.tf_clk :  used to define actual duration of functional form
    if self.tf is None:
      self.tf     =      duration * dt_clk # use the original form
      self.tf_clk = self.duration          # use the -1 form
    else:
      # besure the subtract off the dt_clk time required as above
      self.tf_clk = int( round( (t*dt_clk + self.tf) / dt_clk ) ) - t - 1
      self.tf     = (self.tf_clk + 1) * dt_clk # store integer corrected version

    if self.dt_input:
      self.dt = int( round(self.dt_input/dt_clk) )
    else:
      self.dt = int(self.tf_clk / self.steps)

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
    return step_iter(ti, self.t+min(self.duration,self.tf_clk), self.dt, self)



class Pulse(ScaledFunction):
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
    super(Pulse, self).__init__()
    self.high     = high
    self.low      = low
    self._from    = None
    self.t        = None
    self.duration = None

  def get_encoding(self, capabilities):
    return 'step'

  def __repr__(self):
    return '{}({}, {})'.format(
      self.name, self.ufmt(self.high), self.ufmt(self.low)
    )

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

class PulseTrain(ScaledFunction):
  """
  Generate a train of pulses over the duration of a waveform element.
  """
  name = 'pulses'
  def __init__(self, n, duty=0.5, high=True, low=None):
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
    """
    super(PulseTrain, self).__init__()
    self.n        = n
    self.duty     = duty
    self.high     = high
    self.low      = low
    self._from    = None
    self.t        = None
    self.duration = None

  def get_encoding(self, capabilities):
    return 'step'

  def __repr__(self):
    return '{}({}, {}, {}, {})' \
      .format(self.name, self.n, self.duty,
              self.ufmt(self.high), self.ufmt(self.low))

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

    self.pulse_period = int(duration / self.n)
    max_dt_on = self.pulse_period - 1

    if self.duty < 0 or self.duty > 1:
      raise RuntimeError('pulses:  duty cycle _must_ be between 0 and 1')
    elif self.duty == 0:
      self.dt_on = 1
    elif self.duty == 1:
      self.dt_on = max_dt_on - 1
    else:
      self.dt_on = int( round(max_dt_on * self.duty) )

    self.dt_off = self.pulse_period - self.dt_on

  def __iter__(self):
    L = list()
    t = self.t
    for i in range(self.n):
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

  def get_encoding(self, capabilities):
    return 'linear' if 'linear' in capabilities else 'step'

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


class Expr(object):
  markup = \
"""
<span color="blue"><b><u>Value Expressions Basics</u></b></span>(sympy expressions available:  {})

The value of each waveform element, in the most basic form, may be specified as
a single value with units appropriate for the respective channel.

Often times, a single value for a waveform element is not sufficient.  Arbwave
provides two mechanisms that allow a single waveform element to represent a
time-varying function.  The simplest of these two is using <i>Value Expressions</i>,
as described in here.  The second mechanism is using the much more
powerful, extensible, but much more complicated-to-extend <i>Value Generators
</i>--see help menu for more information.

If the sympy package is available, Arbwave uses it to allow the user to specify
functional forms of values for a waveform element.  When using expressions, in
order to define how a channel's value should change over time, one uses the
symbol <b><i>x</i></b> to represent relative waveform-element time.  <b><i>x</i></b> always varies
from 0 to 1.  Thus, for a waveform element with duration <b><i>dt</i></b>, <b><i>x</i></b> varies from 0 to 1
over the duration of the waveform element.

As an example of using expressions, consider the <b>Ramp</b> value generator
function.  This function generally varies the channel as:

  U0 + (U1 - U0)*x**E

where U0 and U1 are the beginning and ending values of the ramp respectively and
E is the power of the time dependence.  If, for instance, a voltage channel
required to be changed from its original value to a final value of 10*V with a
square-root time dependence, one could simply use an expression like:

  U0 + (10*V - U0)*x**0.5

Using expressions, it is much simpler for the user to specify somewhat arbitrary
functional forms of waveform values.  For instance, one can specify an Gaussian
change function as something like:

  10*V * sy.exp(-(x-.5)**2.0 / (2 * .1**2.0))

where sy represents the sympy module as imported in the global script as:

  import sympy as sy

<span color="blue"><b><u>Value Expressions Advanced</u></b></span>
Just as many <i>Value Generators</i> allow the user to use functional arguments to
modify the waveform generated, such as the number of steps in a <b>Ramp</b>,
<i>Value Expressions</i> similarly provides a method to modify the output.

There are three primary parameters to modify the resulting waveform of an
expression:
  - <tt>expr_fmt</tt>
    - uniform
      Causes the output waveform to be uniformly discretized in time.
    - optimize
      Causes the output waveform to be optimally discretized in time such that a
      constant total err (<tt>expr_err</tt>) is maintained for each linear
      time segment.
  - <tt>expr_steps</tt>
      For <tt>expr_fmt = uniform</tt>, this sets the number of fixed-size steps
      to make over the duration.
      For <tt>expr_fmt = optimize</tt>, <tt>1/expr_steps</tt> defines the
      minimal relative time-step to consider when creating a line segment that
      maximally incurs a total error equal to <tt>expr_err</tt>.
  - <tt>expr_err</tt>
      See "optimize" above.

There are three possible methods to set each of these <i>Value Expression</i>
parameters:
  - globally (i.e. in embedded Python shell or in global script)
  - local to group (in a local group script)
  - local to waveform element:
    If one desires the scope of these parameters to be limited to a single
    element, one must wrap the expression by the <tt>expr</tt> function.
    The signature to this function is given by:
      <b>expr(expression, steps=None, err=None, fmt=None)</b>
""".format(has_sympy)

  def __init__(self):
    self.settings = Dict()

  def __call__(self, expression, steps=None, err=None, fmt=None):
    if steps is not None:
      self.settings.expr_steps = steps
    if err is not None:
      self.settings.expr_err = err
    if fmt is not None:
      self.settings.expr_fmt = fmt
    return expression

  def update_settings(self, D):
    self.settings.setdefault('expr_steps', D['expr_steps'])
    self.settings.setdefault('expr_err', D['expr_err'])
    self.settings.setdefault('expr_fmt', D['expr_fmt'])


registered = {
  SinPulse.name   : SinPulse,
  Ramp.name       : Ramp,
  Pulse.name      : Pulse,
  PulseTrain.name : PulseTrain,
  Interpolate.name: Interpolate,
}
