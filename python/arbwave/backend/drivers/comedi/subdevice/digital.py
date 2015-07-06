# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
from .....tools.float_range import float_range
from subdevice import Subdevice as Base
import ctypes_comedi as c
import re

class Digital(Base):
  subdev_type = 'do'
  
  
  
  def add_channels(self, aref=c.AREF_GROUND, rng=0):
    
    
    chans = self.channels.items()
    
    #chans.sort( key = lambda v : v[1]['order'] )
    
    i = 0
    
    for ch in chans:
      
      num = re.search('([0-9]*)$', ch[0])
      
      self.cmd_chanlist[i] = c.CR_PACK(int(num.group()), rng, aref)
      self.chan_index_list.append(int(num.group()))
      i += 1
      
    
      
    
