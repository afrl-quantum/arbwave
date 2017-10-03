# vim: ts=2:sw=2:tw=80:nowrap
"""
This module provides the ability to convert and arbitrary waveform shape into a
piecewise linear function.  There are two types of conversion that are
supported:
1)  Piecewise step functions.  This type of piecewise function is particularly
    useful for output channels that are only capable (in hardware) of
    maintaining a fixed value for a single external timestep.  Many commercial
    analog output boards only support this mode.
2)  Piecewise continuous functions.  This type of piecewise function allows for
    line-segments of various slopes to be connected together into a single
    waveform.  This capability is meant to support hardware that has built-in
    capability to vary the output based on a fixed slope per external timestep.
    Direct Digital Synthesis hardware often has this capability.  Additionally,
    the NIST Pretty Darn Quick (PDQ) analog output hardware designs support
    something of this fashion (although they also support non-fixed slopes
    between points).
"""

import numpy as np
from itertools import izip, repeat

from physical.sympy_util import has_sympy, from_sympy

if has_sympy:
  import sympy

from ...tools.float_range import xarange

machine_arch = np.MachAr()



def calculate_piecewise_step(xmin, xmax, xstep, func, err_max):
  b = float(func(xmin))
  x = min(xmin + xstep, xmax)
  xL = list()
  err = 0
  while x < xmax:
    xL.append(x - 0.5*xstep)
    err = sum([abs(float(func(xi)) - b) for xi in xL])
    if err >= err_max or abs(xmax-x) < 10*machine_arch.eps:
      break
    x = min(x + xstep, xmax)
  return x, err

def calculate_piecewise_line(xmin, xmax, xstep, func, err_max):
  b = float(func(xmin))
  x = min(xmin + xstep, xmax)
  xL = list()
  err = 0
  while x < xmax:
    xL.append(x - 0.5*xstep)
    m = (float(func(x)) - b) / (x - xmin)
    err = sum([abs(float(func(xi)) - (m*(xi-xmin)+b)) for xi in xL])
    if err >= err_max or abs(xmax-x) < 10*machine_arch.eps:
      break
    x = min(x + xstep, xmax)
  return x, err

def _create_piecewise_impl(sub_func, name, typ, segs):
  def calculate_linear_piecewise(xmin, xmax, xstep, func, err_max):
    """
    Calculate the piecewise {} function for the given function.

    This calculation attempts to keep the error below a user-supplied value for
    each piecewise section.

    This implementation connects points together with {} segments.
    """
    points = [(xmin,0)]
    x = xmin
    while x < xmax:
      x, err = sub_func(x, xmax, xstep, func, err_max)
      points.append((x,err))
    return points
  calculate_linear_piecewise.__doc__ = \
    calculate_linear_piecewise.__doc__.format(typ,segs)
  calculate_linear_piecewise.__name__ = 'calculate_{}_piecewise'.format(name)

  return calculate_linear_piecewise

calculate_step_piecewise = \
  _create_piecewise_impl(calculate_piecewise_step,
                         'step', 'step', 'constant value')

calculate_cont_piecewise = \
  _create_piecewise_impl(calculate_piecewise_line,
                         'cont', 'continuous', 'constant slope')



def optimize(expression, ti, dti, expr_steps, expr_err,
             channel_scale, channel_caps, channel_units, **kw):
  if 'linear' in channel_caps:
    calc = calculate_cont_piecewise
  elif 'step' in channel_caps:
    calc = calculate_step_piecewise
  else:
    raise NotImplementedError('Channel does not have any reasonable capabilities')

  dx = 1./expr_steps

  # calculate & cache all values of the expression that will be used
  xsym = sympy.Symbol('x')
  cache = tuple(
    from_sympy(expression.subs(xsym,x), channel_units)
    for x in xarange(0,1+10*machine_arch.eps,0.5*dx)
  )

  # this function will simply lookup expression values in the cache
  def func(x):
    return cache[int(x)]

  #calculate the time spacing
  err_max = expr_err * channel_scale
  xL = calc(0, 2*expr_steps, 2, func, err_max)

  # now convert the time spacing into (tij, dtij, v(tij)) tuples
  for (x0, err0), (x1, err1) in izip(xL[:-1], xL[1:]):
    x0f = x0 / (2.*expr_steps)
    x1f = x1 / (2.*expr_steps)
    yield int(round(ti + x0f*(dti-1))), int((x1f-x0f)*(dti-1)), func(x0)

  yield ti + (dti-1), 1, func(2*expr_steps)


def uniform(expression, ti, dti, expr_steps, channel_units, **kw):
  """
  Uniformly discretize the integer _and_ fractional relative time.  This
  function is to help generate values from a sympy expression for waveform
  elements.

  ti: absolute time in units of dt_clk for the particular channel.
  dti: duration in units of dt_clk for the particular channel.
  expr_steps: number of fixed-size steps to make over the duration.

  returns an iterator of tuples of the form:
    (section time/dt_clk, section duration/dt_clk, relative time of section)
  """
  dtij = 1 if dti < expr_steps else (dti/expr_steps) # step size for integer time
  dx = dtij/float(dti) # step size for relative (0-1) time

  xsym = sympy.Symbol('x')
  for tij, x in izip( xrange(ti, ti+dti-1 - dtij, dtij),
                     xarange(0, 1, dx)):

    yield tij, dtij, from_sympy(expression.subs(xsym, x), channel_units)

  # second to last transition. Make sure it is not too long
  yield tij+dtij, min(dtij, ti+dti-1 - (tij+dtij)), \
        from_sympy(expression.subs(xsym,x+dx), channel_units)

  # last point is added very explicitly to reach the end of time (x=1)
  yield ti+dti-1, 1, from_sympy(expression.subs(xsym,1), channel_units)



evaluators = dict(
  uniform   = uniform,
  optimize  = optimize
)
