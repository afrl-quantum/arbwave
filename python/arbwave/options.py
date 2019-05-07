# vim: ts=2:sw=2:tw=80:nowrap
"""
Storage for persistent command-line options.
"""

simulated = False

ipython = False

# set of drivers that have been requested by the user to disable
disabled_drivers = set()

pyro_ns = None


pyro_resync_set = set()

def set_pyro_nameserver(ns):
  global pyro_ns
  pyro_ns = ns

  for i in pyro_resync_set:
    i.resync_ns()

# pstats.Stats object to accumulate profile statistics into (if not None)
pstats = None
