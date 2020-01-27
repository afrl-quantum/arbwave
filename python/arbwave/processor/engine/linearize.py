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
from logging import log, info, debug, warn, critical, DEBUG, root as rootlog

from physical.sympy_util import has_sympy

if has_sympy:
  import sympy

from ...tools.float_range import xarange

machine_arch = np.MachAr()



def calculate_piecewise_step(imin, imax, cache, err_max):
  # this function expects a cache sampling rate equal to the 1/expr_steps
  b = cache[imin]
  ilast = imin
  err_last = 0
  for i in range(imin + 1, imax + 1):
    err = abs(cache[i] - b)
    if err > err_max:
      break
    ilast = i
    err_last = err

  if ilast == imin:
    raise RuntimeError(
      'expr_steps to small to provide minimum expression error'
    )
  return ilast, err_last

def calculate_piecewise_line(imin, imax, cache, err_max):
  """
  Calculate the next step for a piecewise line expression.

  As opposed to the method used for step functions (calculate_piecewise_step),
  this functions expects twice the cache sampling rate as the minimum step.
  This twice sampling rate is used to at least provide some level of error
  detection between each of the linear pieces, even though the maximal number of
  linear components is given by the user's specified value for expr_steps.
  """
  b = cache[imin]
  ilast = imin
  err_last = 0

  # stride for following loop is 2 so that segments always align to
  # user-specified steps.
  for i in range(imin + 2, imax+1, 2):
    # test every cached point along the line segment and find the max error
    m = (cache[i] - b) / (i - imin)
    err = max([
      abs(cache[ii] - (m*(ii-imin)+b))
      for ii in range(imin + 1, i) # don't test end points that have zero error
    ])
    if err > err_max:
      break
    ilast = i
    err_last = err

  if ilast == imin:
    raise RuntimeError(
      'expr_steps to small to provide minimum expression error'
    )
  return ilast, err_last

def _create_piecewise_impl(sub_func, name, typ, segs):
  def calculate_linear_piecewise(imin, imax, cache, err_max):
    """
    Calculate the piecewise {} function for the given function.

    This calculation attempts to keep the error below a user-supplied value for
    each piecewise section.

    This implementation connects points together with {} segments.
    """
    points = [(imin,0)]
    i = imin
    while i < imax:
      i, err = sub_func(i, imax, cache, err_max)
      points.append((i,err))
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



def optimize(expression, ti, dti, expr_steps, expr_err, channel_caps,
             channel_units, **kw):
  """
  expression:  a sympy.lambdify'd, simplified, unitless version of the original
               sympy expression (to enhance the execution speed).  The only
               argument of the numpy.lambda function is x.
  ti: absolute time in units of dt_clk for the particular channel.
  dti: duration in units of dt_clk for the particular channel.
  expr_steps: number of fixed-size steps to make over the duration.

  returns an iterator of tuples of the form:
    (section time/dt_clk, section duration/dt_clk, relative time of section)
  """
  if 'linear' in channel_caps:
    calc = calculate_cont_piecewise
  elif 'step' in channel_caps:
    calc = calculate_step_piecewise
    expr_steps = expr_steps * 2 # twice sampling rate for error estimation
  else:
    raise NotImplementedError('Channel does not have any reasonable capabilities')

  dx = 1. / expr_steps

  # calculate & cache all unitless values of the expression that will be used
  cache = expression(np.r_[0:(1+10*machine_arch.eps):dx])
  err_max = expr_err * (cache.max() - cache.min())

  #calculate the time spacing
  iL = calc(0, expr_steps, cache, err_max)

  # now convert the time spacing into (tij, dtij, v(tij)) tuples
  for (i0, err0), (i1, err1) in zip(iL[:-1], iL[1:]):
    x0f = i0 / expr_steps
    x1f = i1 / expr_steps
    yield int(round(ti + x0f*(dti-1))), \
          int((x1f-x0f)*(dti-1)), \
          cache[i0] * channel_units

  yield ti + (dti-1), 1, cache[expr_steps] * channel_units


def uniform(expression, ti, dti, expr_steps, channel_units, **kw):
  """
  Uniformly discretize the integer _and_ fractional relative time.  This
  function is to help generate values from a sympy expression for waveform
  elements.

  expression:  a sympy.lambdify'd, simplified, unitless version of the original
               sympy expression (to enhance the execution speed).  The only
               argument of the numpy.lambda function is x.
  ti: absolute time in units of dt_clk for the particular channel.
  dti: duration in units of dt_clk for the particular channel.
  expr_steps: number of fixed-size steps to make over the duration.

  returns an iterator of tuples of the form:
    (section time/dt_clk, section duration/dt_clk, relative time of section)
  """
  # dtij: step size for integer time
  dtij = 1 if dti < expr_steps else int(dti/expr_steps)
  dx = dtij/float(dti) # step size for relative (0-1) time

  for tij, x, val in zip(range(ti, ti+dti-1 - dtij, dtij),
                         xarange(0, 1, dx),
                         expression(np.r_[0:1:dx])):
    yield tij, dtij, val * channel_units

  # second to last transition. Make sure it is not too long
  yield tij+dtij, min(dtij, ti+dti-1 - (tij+dtij)), \
        expression(x+dx) * channel_units

  # last point is added very explicitly to reach the end of time (x=1)
  yield ti+dti-1, 1, expression(1) * channel_units



evaluators = dict(
  uniform   = uniform,
  optimize  = optimize
)
