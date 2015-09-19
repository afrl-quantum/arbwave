# vim: ts=2:sw=2:tw=80:nowrap

from .. import ctypes_comedi as comedi

#### comedi_range ####
def comedi_range_to_dict(self):
  D = {
    i:getattr(self,i) for i in dir(self)
      if i[0] != '_' and not callable(getattr(self,i))
  }

  D['unit'] = {
    comedi.UNIT_mA: 'mA',
    comedi.UNIT_none: None,
    comedi.UNIT_volt: 'V',
  }[ self.unit ]
  return D

def comedi_range_repr(self):
  return repr( self.dict() )

comedi.comedi_range.dict = comedi_range_to_dict
comedi.comedi_range.__repr__ = comedi_range_repr
