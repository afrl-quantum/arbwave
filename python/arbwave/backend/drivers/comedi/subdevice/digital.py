# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
import re
from .. import ctypes_comedi as clib

from .....tools.float_range import float_range
from .subdevice import Subdevice as Base

class Digital(Base):
  subdev_type = 'do'

  def add_channels(self, aref=clib.AREF_GROUND, rng=0):
    chans = self.channels.items()

    #chans.sort( key = lambda v : v[1]['order'] )

    for i, ch in zip( xrange(len(chans)), chans ):
      num = re.search('([0-9]*)$', ch[0])

      self.cmd_chanlist[i] = clib.CR_PACK(int(num.group()), rng, aref)
      self.chan_index_list.append(int(num.group()))


  def set_output(self, data):
    data = clib.lsampl_t(0)
    write_mask = 0
    for chname, value in data.items():
      ch = self.get_channel( chname )
      data.value |= bool(value) << ch
      write_mask |= 1 << ch

    clib.comedi_dio_bitfield2(
      self.card,
      self.subdevice,
      write_mask,
      byref(bits),
      base_channel=0,
    )
