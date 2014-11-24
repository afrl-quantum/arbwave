# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated low-level comedilib library.
"""

import comedi as c
from logging import log, debug, info, warn, error, critical, DEBUG

def inject_sim_lib():
  c._comedi = ComediSim()
  import_funcs = [ f for f in dir(c._comedi) if f.startswith('comedi')]
  for f in import_funcs:
    setattr( c, f, getattr(c._comedi,f) )

class ComediSim(object):

  def comedi_open(self, filename):
    return 0 # FIXME:  return the right type of value(?)

  def comedi_find_subdevice_by_type(self, fd, typ, start_subdevice):
    return start_subdevice

  def comedi_get_cmd_src_mask(self, fd, index, cmd):
    raise NotImplementedError('finish this...')
    return 0

  def comedi_get_driver_name(self, fd):
    return 'ni_pcimio'

  def comedi_get_board_name(self, fd):
    return 'pxi-6733'
