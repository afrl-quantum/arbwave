# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
import re
from .. import ctypes_comedi as clib

from .....tools.float_range import float_range
from .subdevice import Subdevice as Base

class Analog(Base):
  subdev_type = 'ao'
  

  def add_channels(self, aref=clib.AREF_GROUND, rng=0):
    # populate the task with output channels and accumulate the data
    dflt_mn = self.config['default-voltage-range']['minimum']['value']
    dflt_mx = self.config['default-voltage-range']['maximum']['value']
    
    chans = self.channels.items()
    
    #chans.sort( key = lambda v : v[1]['order'] )
    
 
    i = 0
    
    for ch in chans:
      print ch
      if ch[1]:
        mn, mx = ch[1]['min'], ch[1]['max']
      else:
        # use the default range values
        mn, mx = dflt_mn, dflt_mx
      
      num = re.search('([0-9]*)$', ch[0])

      #rng = clib.comedi_find_range(self.card, self.subdevice, int(num.group()),clib.UNIT_volt,mn,mx)
      # references to self.card nside of comedi functions only work in subdevice.py why?
      
      self.cmd_chanlist[i] = clib.CR_PACK(int(num.group()), rng, aref)
      self.chan_index_list.append(int(num.group()))
      i += 1
      
    
     


  def get_config_template(self):
    template = Base.get_config_template(self)
    template['default-voltage-range'] = {
      'minimum' : {
        'value' : -10.0,
        'type'  : float,
        'range' : float_range(-10.0, 10.0),
      },
      'maximum' : {
        'value' : 10.0,
        'type'  : float,
        'range' : float_range(-10.0, 10.0),
      },
    }
    return template
