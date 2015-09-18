# vim: ts=2:sw=2:tw=80:nowrap

from .. import ctypes_comedi as comedi

insn_map = { i:getattr(comedi,i) for i in dir(comedi) if i.startswith('INSN') }
insn_rmap= { v:k for k,v in insn_map.items() }

#### comedi_insn ####
def comedi_insn_to_dict(self):
  D = {
    i:getattr(self,i) for i in dir(self)
      if i[0] != '_' and not callable(getattr(self,i))
  }

  D['insn'] = insn_rmap[ self.insn ]
  D['data'] = self.data[:self.n]
  D['unused'] = self.unused[:]
  D['chanspec'] = \
    dict( channel = comedi.CR_CHAN(self.chanspec),
             aref = comedi.CR_AREF(self.chanspec),
            range = comedi.CR_RANGE(self.chanspec) )

  return D

def comedi_insn_repr(self):
  return repr( self.dict() )

comedi.comedi_insn.dict = comedi_insn_to_dict
comedi.comedi_insn.__repr__ = comedi_insn_repr




#### comedi_insnlist ####
def comedi_insnlist_to_dict(self):
  return dict(
    insns = self.insns[:self.n_insns],
    n_insns = self.n_insns,
  )

def comedi_insnlist_repr(self):
  return repr( self.dict() )

def comedi_insnlist_getitem(self, i):
  return self.insns[i]

def comedi_insnlist_iter(self):
  return iter( self.insns[:self.n_insns] )

def comedi_insnlist_set_length(self, length):
  old_insns = None
  if hasattr(self, '_self_made') and getattr(self,'_self_made'):
    old_insns = self.insns

  self.n_insns = length
  self.insns = (comedi.comedi_insn * length)()
  self._self_made = True

  if old_insns:
    # free the old memory
    del old_insns


comedi.comedi_insnlist.dict = comedi_insnlist_to_dict
comedi.comedi_insnlist.__repr__ = comedi_insnlist_repr
comedi.comedi_insnlist.__getitem__ = comedi_insnlist_getitem
comedi.comedi_insnlist.__iter__ = comedi_insnlist_iter
comedi.comedi_insnlist.set_length = comedi_insnlist_set_length
