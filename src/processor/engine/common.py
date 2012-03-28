# vim: ts=2:sw=2:tw=80:nowrap

global_load = \
"""
if globals is None:
  import inspect
  globals = inspect.stack()[2][0].f_globals
"""

