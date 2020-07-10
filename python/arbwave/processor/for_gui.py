# vim: ts=2:sw=2:tw=80:nowrap
"""
This is the specialization of the processor that helps with integration into
the gui.
"""

import sys
from . import base
from . import messages as msg

class Processor(base.Processor):
  def __init__(self, ui):
    super(Processor,self).__init__(ui)
    sys.modules['msg'] = msg
    msg.set_main_window( ui )
