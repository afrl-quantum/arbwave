# vim: ts=2:sw=2:tw=80:nowrap
"""
Default environment settings.
"""

from ..float_range import float_range
import functions

registered_globals = {
  'float_range' : float_range,
}

registered_globals.update( functions.registered )

def get_globals():
  return registered_globals.copy()
