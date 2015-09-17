from comedi import *
from ctypeslib_comedi import *


# fix up some things for convenience

def comedi_cmd_to_dict(self):
  D = {
    i:getattr(self,i) for i in dir(self)
      if i[0] != '_' and not callable(getattr(self,i))
  }

  D['chanlist'] = tuple(
    dict( channel = CR_CHAN(self.chanlist[i]),
             aref = CR_AREF(self.chanlist[i]),
            range = CR_RANGE(self.chanlist[i]) )
    for i in xrange( self.chanlist_len )
  )

  return D

def comedi_cmd_repr(self):
  return repr( self.dict() )

comedi_cmd.dict = comedi_cmd_to_dict
comedi_cmd.__repr__ = comedi_cmd_repr
