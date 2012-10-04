# vim: ts=2:sw=2:tw=80:nowrap

import physical

class AssurePrintStyle:
  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs

  def __call__(self, arg):
    try:
      for u in arg:
        if type(u) is physical.Quantity:
          u.set_print_style(*self.args, **self.kwargs)
      return arg
    except TypeError:
      if type(arg) is physical.Quantity:
        arg.set_print_style(*self.args, **self.kwargs)
      return arg

M = AssurePrintStyle('math')
LO = AssurePrintStyle('latex')
L = AssurePrintStyle('latex', oneline=False)
U = AssurePrintStyle('ugly')
P = AssurePrintStyle('pretty')
