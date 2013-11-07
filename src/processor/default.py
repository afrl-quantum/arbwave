# vim: ts=2:sw=2:tw=80:nowrap
"""
Default environment settings.
"""

import numpy as np
from ..tools.float_range import float_range, xarange
import functions

registered_globals = {
  'float_range' : float_range,
  'xarange' : xarange,
  'arange'  : np.arange,
  'r_'      : np.r_,
  'inf'     : float('inf'),
  'nan'     : float('nan'),
  '_kwargs' : dict(),
}

registered_globals.update( functions.registered )

def get_globals():
  return registered_globals.copy()
