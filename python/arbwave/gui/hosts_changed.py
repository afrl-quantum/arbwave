# vim: ts=2:sw=2:tw=80:nowrap
"""
These routines provide a hack method of fixing up user interface when the hosts
have changed.  Essentially, after a host connection has changed, a list of
functions, as defined by individual modules, is executed.
"""

callbacks = list()

def callback():
  for c in callbacks: c()
