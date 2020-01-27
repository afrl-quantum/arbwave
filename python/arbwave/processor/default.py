# vim: ts=2:sw=2:tw=80:nowrap
"""
Default environment settings.
"""

import numpy as np
from physical.sympy_util import has_sympy
from ..tools.float_range import float_range, xarange
from . import functions

registered_globals = {
  'float_range' : float_range,
  'xarange' : xarange,
  'arange'  : np.arange,
  'r_'      : np.r_,
  'inf'     : float('inf'),
  'nan'     : float('nan'),
  '_kwargs' : dict(),
}

if has_sympy:
  registered_globals.update(dict(
    expr_steps = 10,
    expr_err   = 0.1,
    expr_fmt   = 'uniform',
  ))

registered_globals.update( functions.registered )

def get_globals():
  return registered_globals.copy()
