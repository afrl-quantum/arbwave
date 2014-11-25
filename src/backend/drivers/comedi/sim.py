# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated low-level comedilib library.
"""

import comedi as c
from logging import log, debug, info, warn, error, critical, DEBUG
import re

def inject_sim_lib():
  C = ComediSim()
  import_funcs = [ f for f in dir(C) if f.startswith('comedi')]
  for f in import_funcs:
    setattr( c, f, getattr(C,f) )


class SimDevice(object):
  driver  = None
  board   = None
  def comedi_find_subdevice_by_type(self, typ, start_subdevice):
    if start_subdevice < 0:
      raise OverflowError('comedi_find_subdevice_by_type: start_subdevice >=0!')
    k = [ k for k,v in self.subdevs.items() if v['typ'] == typ ]
    if len(k) == 0 or start_subdevice > max(k):
      log(DEBUG-1,'returning subdev: -1')
      return -1
    while start_subdevice not in k:
      start_subdevice += 1
    log(DEBUG-1,'returning subdev: %d', start_subdevice)
    return start_subdevice

  def comedi_get_cmd_src_mask(self, subdev, cmd):
    # this is at least for the analog subdev of the PXI-6733
    for a,v in self.subdevs[subdev]['cmd'].items(): setattr( cmd, a, v )
    return 0

  def comedi_get_subdevice_flags(self, subdev):
    return self.subdevs[subdev]['flags']


class PXI_6733(SimDevice):
  driver = 'ni_pcimio'
  board = 'pxi-6733'
  subdevs = {
    1 : dict( typ=c.COMEDI_SUBD_AO, flags=34754560,
      cmd=dict(chanlist=None,
               chanlist_len=0,
               convert_arg=0,
               convert_src=2,
               data=None,
               data_len=0,
               flags=64,
               scan_begin_arg=0,
               scan_begin_src=80,
               scan_end_arg=0,
               scan_end_src=32,
               start_arg=0,
               start_src=192,
               stop_arg=0,
               stop_src=33,
               subdev=1,
      ),
    ),
  }

class PXI_6723(PXI_6733):
  pass


class ComediSim(object):
  def __init__(self):
    self.devices = {
      0 : PXI_6733(),
      1 : PXI_6723(),
    }

  def comedi_open(self, filename):
    debug('comedi_open(%s)', filename)
    m = re.match( '/dev/comedi(?P<device>[0-9]+)$', filename )
    if not m or int(m.group('device')) not in self.devices: return None
    return int(m.group('device')) # FIXME:  return the right type of value(?)

  def comedi_close(self, fd):
    debug('comedi_close(%d)', fd)
    return 0

  def comedi_find_subdevice_by_type(self, fd, typ, start_subdevice):
    debug('comedi_find_subdevice_by_type(%d, %d, %d)', fd,typ,start_subdevice)
    if fd not in self.devices: return -1
    return self.devices[fd].comedi_find_subdevice_by_type(typ, start_subdevice)

  def comedi_get_cmd_src_mask(self, fd, index, cmd):
    debug('comedi_get_cmd_src_mask(%d, %d, %s)', fd, index, cmd)
    if fd not in self.devices: return -1
    return self.devices[fd].comedi_get_cmd_src_mask(index, cmd)

  def comedi_get_subdevice_flags(self, fd, subdev):
    debug('comedi_get_subdevice_flags(%d, %d)', fd, subdev)
    if fd not in self.devices: return -1
    return self.devices[fd].comedi_get_subdevice_flags(subdev)

  def comedi_get_driver_name(self, fd):
    return self.devices[fd].driver

  def comedi_get_board_name(self, fd):
    return self.devices[fd].board

  def comedi_cancel(self, fd, subdev):
    debug('comedi_cancel(%d, %d)', fd, subdev)
    return 0
