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
    debug('comedi_open(%s)', filename)
    return 0 # FIXME:  return the right type of value(?)

  def comedi_close(self, fd):
    debug('comedi_close(%d)', fd)
    return 0

  def comedi_find_subdevice_by_type(self, fd, typ, start_subdevice):
    debug('comedi_find_subdevice_by_type(%d, %d, %d)', fd,typ,start_subdevice)
    if start_subdevice < 0:
      raise OverflowError('comedi_find_subdevice_by_type: start_subdevice >=0!')
    if   start_subdevice <= 1 and typ == c.COMEDI_SUBD_AO:
      return 1
    elif start_subdevice <= 2 and typ == c.COMEDI_SUBD_DO:
      return 2
    elif start_subdevice <= 3 and typ == c.COMEDI_SUBD_DIO:
      return 3
    elif start_subdevice <= 4 and typ == c.COMEDI_SUBD_COUNTER:
      return 4
    return -1

  def comedi_get_cmd_src_mask(self, fd, index, cmd):
    # this is at least for the analog subdev of the PXI-6733
    cmd = c.comedi_cmd_struct()
    for a,v in [('chanlist', None),
                ('chanlist_len', 0),
                ('convert_arg', 0),
                ('convert_src', 2),
                ('data', None),
                ('data_len', 0),
                ('flags', 64),
                ('scan_begin_arg', 0),
                ('scan_begin_src', 80),
                ('scan_end_arg', 0),
                ('scan_end_src', 32),
                ('start_arg', 0),
                ('start_src', 192),
                ('stop_arg', 0),
                ('stop_src', 33),
                ('subdev', 1),
     ]: setattr( cmd, a, v )
    return 0

  def comedi_get_driver_name(self, fd):
    return 'ni_pcimio'

  def comedi_get_board_name(self, fd):
    return 'pxi-6733'

  def comedi_cancel(self, fd, subdev):
    debug('comedi_cancel(%d, %d)', fd, subdev)
    return 0

  def comedi_get_subdevice_flags(self, fd, subdev):
    debug('comedi_get_subdevice_flags(%d, %d)', fd, subdev)
    # value returned for pxi-6733 analog subdev
    return 34754560
