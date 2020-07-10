# vim: ts=2:sw=2:tw=80:nowrap
"""
This is the specialization of the processor that helps with integration into
the gui.
"""

import sys
from . import base
from ..tools.dict import Dict

class Processor(base.Processor):
  def __init__(self, ui, globals=dict(), arbweng=None):
    super(Processor,self).__init__(ui, globals, arbweng)
    sys.modules['msg'] = Msg


buttons_map = {
  'ok-cancel' : Dict(text='[O]k/[C]ancel [O]: ', ok=['O','o'], nok=['C','c'], default='o'),
  'ok'        : Dict(text='[O]k [O]: ', ok=['O','o'], nok=[], default='o'),
  'cancel'    : Dict(text='[C]ancel [C]: ', ok=[], nok=['C','c'], default='c'),
  'close'     : Dict(text='[C]lose [C]: ', ok=[], nok=['C','c'], default='c'),
  'yes-no'    : Dict(text='[Y]es/[N]o [Y]: ', ok=['Y','y'], nok=['N','n'], default='y'),
  None        : Dict(ok=[], nok=[]),
}

class Msg(object):
  # text versions of gui message handling
  @staticmethod
  def info(msg, type='info', buttons='ok-cancel', ignore_result=False):
    B = buttons_map[buttons]
    ANS = B.ok + B.nok
  
    print(type.upper(), ': ', msg)
  
    if ANS:
      ans = None
      while ans not in ANS:
        ans = input(B.text) or B.default
  
      if ans in B.nok:
        raise RuntimeError('Stop')
  
  @classmethod
  def warn(cls, msg, buttons='ok-cancel', **kwargs):
    return cls.info(msg, 'warn', buttons, **kwargs)
  
  @classmethod
  def error(cls, msg, buttons='ok-cancel', **kwargs):
    return cls.info(msg, 'error', buttons, **kwargs)
  
  @classmethod
  def ask(cls, msg, buttons='yes-no', **kwargs):
    return cls.info(msg, 'ask', buttons, **kwargs)
