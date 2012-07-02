# vim: ts=2:sw=2:tw=80:nowrap

from numpy import MachAr

machine_arch = MachAr()
def cmpeps( a, b, scale_eps=1.0 ):
  if a < (b-machine_arch.eps*scale_eps):
    return -1
  elif a > (b+machine_arch.eps*scale_eps):
    return 1
  else:
    return 0

