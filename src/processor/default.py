# vim: ts=2:sw=2:tw=80:nowrap
"""
Default environment settings.
"""

from ..float_range import float_range

def get_globals():
  return {
    'float_range' : float_range,
  }
