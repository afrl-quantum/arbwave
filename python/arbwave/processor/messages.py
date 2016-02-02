# vim: ts=2:sw=2:tw=80:nowrap
"""
Implements message dialogs for use in scripts.
"""

from gi.repository import Gtk as gtk
from ..tools.gui_callbacks import do_gui_operation

main_window = None

def set_main_window( mw ):
  global main_window
  main_window = mw

type_map = {
  'info'    : gtk.MessageType.INFO,
  'warn'    : gtk.MessageType.WARNING,
  'warning' : gtk.MessageType.WARNING,
  'error'   : gtk.MessageType.ERROR,
  'ask'     : gtk.MessageType.QUESTION,
}

buttons_map = {
  'ok-cancel' : gtk.ButtonsType.OK_CANCEL,
  'ok'        : gtk.ButtonsType.OK,
  'cancel'    : gtk.ButtonsType.CANCEL,
  'close'     : gtk.ButtonsType.CLOSE,
  'yes-no'    : gtk.ButtonsType.YES_NO,
  None        : gtk.ButtonsType.NONE,
}

response_map = {
  gtk.ResponseType.ACCEPT : 'accept',
  gtk.ResponseType.APPLY  : 'apply',
  gtk.ResponseType.CANCEL : 'cancel',
  gtk.ResponseType.CLOSE  : 'close',
  gtk.ResponseType.NO     : 'no',
  gtk.ResponseType.OK     : 'ok',
  gtk.ResponseType.REJECT : 'reject',
  gtk.ResponseType.YES    : 'yes',
  gtk.ResponseType.NONE   : None,
}

import time

class Show:
  def __init__(self):
    self.retval = None
    self.retval_valid = False

  def __call__(self, msg, type, buttons):
    d = gtk.MessageDialog( main_window,
      gtk.DialogFlags.MODAL | gtk.DialogFlags.DESTROY_WITH_PARENT,
      type_map[type], buttons_map[buttons] )
    d.set_markup( msg )
    try:
      self.retval = response_map.get(d.run(), None)
      self.retval_valid = True
    finally:
      d.destroy()

  def result(self):
    while not self.retval_valid:
      time.sleep(.1)
    return self.retval


def info(msg, type='info', buttons='ok-cancel', ignore_result=False):
  s = Show()
  do_gui_operation(s, msg, type, buttons)
  if not ignore_result:
    return s.result()

def warn(msg, buttons='ok-cancel', **kwargs):
  return info(msg, 'warn', buttons, **kwargs)

def error(msg, buttons='ok-cancel', **kwargs):
  return info(msg, 'error', buttons, **kwargs)

def ask(msg, buttons='yes-no', **kwargs):
  return info(msg, 'ask', buttons, **kwargs)
