#!/usr/bin/env python

import numpy as np
from pylab import *

class ramp(object):
  def __init__(self, _from, to, exponent, dt):
    self._from = float(_from)
    self.to = float(to)
    self.exponent = float(exponent)
    self.dt = float(dt)
    self.it = 0
  def fun(self, x):
    return self._from + (self.to - self._from)*(x/self.dt)**self.exponent

  @property
  def dy(self):
    return abs(self._from - self.to)

  def __call__(self, x):
    self.it += 1
    if type(x) in [np.ndarray, list]:
      _froms = np.argwhere( x < 0 )
      tos = np.argwhere( x >= self.dt )
      retval = self.fun(x)
      retval[_froms] = self._from
      retval[tos] = self.to
      return retval
    else:
      if x < 0:
        return self._from
      elif x >= self.dt:
        return self.to
      else:
        return self.fun(x)
  #__call__ = fun

class Sine(object):
  dy = 1.0
  def __call__(self,x):
    return np.sin(x)

class Gaussian(object):
  dy = 1.0
  def __init__(self, x0, sigma):
    self.x0 = x0
    self.sigma = sigma

  def __call__(self,x):
    return np.exp(-((x - self.x0)/self.sigma)**2.0 /2)


class Maxwell(object):
  dy = 50.0
  def __call__(self,x):
    return np.log(sqrt(x+0.0001)) - np.exp(-(x-50)**2.0)


machine_arch = np.MachAr()

def calculate_piecewise_section(xmin, xmax, dx, fun, err_max, Err):
  b = fun(xmin)
  x = min(xmin + dx, xmax)
  xL = list()
  err = 0
  while x < xmax:
    xL.append(x - 0.5*dx)
    ferr = Err(fun, x, b, xmin)
    err = sum([abs(fun(xi) - ferr(xi)) for xi in xL])
    if err >= err_max or abs(xmax-x) < 10*machine_arch.eps:
      break
    x = min(x + dx, xmax)
  return x, err

def calculate_linear_piecewise(xmin, xmax, dx, fun, err_max, stepwise):
  if stepwise:
    class Err(object):
      def __init__(self, fun, x0, b, xmin):
        self.b = b
      def __call__(self, x):
        return self.b
  else:
    class Err(object):
      def __init__(self, fun, x0, b, xmin):
        self.m = (fun(x0) - b) / (x0 - xmin)
        self.b = b
        self.xmin = xmin
      def __call__(self, x):
        return self.m*(x - self.xmin) + self.b

  lines = [(xmin, 0)]
  x = xmin
  while x < xmax:
    t = calculate_piecewise_section(x, xmax, dx, fun, err_max, Err)
    lines.append(t)
    x = t[0]
  return np.array(lines)


def main(fun, dx=1/2., err_max=0.01*2, stepwise=False):
  x = np.r_[0:100]
  err_max = fun.dy * err_max
  D = calculate_linear_piecewise(min(x), max(x), dx, fun, err_max, stepwise)
  subplot(2,1,1)
  hold(False)
  plot(x, fun(x), '-')
  hold(True)
  errorbar(D[:,0], fun(D[:,0]), yerr=D[:,1]*.1, fmt='-o')
  hold(False)
  subplot(2,1,2)
  hold(False)
  funDD = lambda x: abs(-sin(x))
  plot(x, np.cumsum(funDD(x)), D[:,0], interp(D[:,0], x, np.cumsum(funDD(x))), 'o')
  show()


from argparse import ArgumentParser
if __name__ == '__main__':
  p = ArgumentParser()
  p.add_argument('--dx',      default=1/2., type=float)
  p.add_argument('--err_max', default=0.01*2, type=float)
  p.add_argument('--stepwise',action='store_true')

  p.add_argument('--ramp',    action='store_true')
  p.add_argument('--_from',   default=2, type=float)
  p.add_argument('--to',      default=50, type=float)
  p.add_argument('--exp',     default=.25, type=float)
  p.add_argument('--dt',      default=10, type=float)

  p.add_argument('--gaussian',action='store_true')
  p.add_argument('--x0',      default=50.0, type=float)
  p.add_argument('--sigma',   default=25.0, type=float)

  p.add_argument('--maxwell', action='store_true')

  args = p.parse_args()

  if args.ramp:
    #ramp args: _from, to, exponent, dt
    fun = ramp(args._from,args.to,args.exp,args.dt)
  elif args.gaussian:
    fun = Gaussian(args.x0,args.sigma)
  elif args.maxwell:
    fun = Maxwell()
  else:
    fun = Sine()
  main(fun, args.dx, args.err_max, args.stepwise)
