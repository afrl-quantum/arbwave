# vim: ts=2:sw=2:tw=80:nowrap
"""
Implements message dialogs for use in scripts.
"""

import gtk
from ..tools.gui_callbacks import do_gui_operation

main_window = None

def set_main_window( mw ):
  global main_window
  main_window = mw

type_map = {
  'info'    : gtk.MESSAGE_INFO,
  'warn'    : gtk.MESSAGE_WARNING,
  'warning' : gtk.MESSAGE_WARNING,
  'error'   : gtk.MESSAGE_ERROR,
  'ask'     : gtk.MESSAGE_QUESTION,
}

buttons_map = {
  'ok-cancel' : gtk.BUTTONS_OK_CANCEL,
  'ok'        : gtk.BUTTONS_OK,
  'cancel'    : gtk.BUTTONS_CANCEL,
  'close'     : gtk.BUTTONS_CLOSE,
  'yes-no'    : gtk.BUTTONS_YES_NO,
  None        : gtk.BUTTONS_NONE,
}

response_map = {
  gtk.RESPONSE_ACCEPT : 'accept',
  gtk.RESPONSE_APPLY  : 'apply',
  gtk.RESPONSE_CANCEL : 'cancel',
  gtk.RESPONSE_CLOSE  : 'close',
  gtk.RESPONSE_NO     : 'no',
  gtk.RESPONSE_OK     : 'ok',
  gtk.RESPONSE_REJECT : 'reject',
  gtk.RESPONSE_YES    : 'yes',
  gtk.RESPONSE_NONE   : None,
}

import time

class Show:
  def __init__(self):
    self.retval = None
    self.retval_valid = False

  def __call__(self, msg, type, buttons):
    d = gtk.MessageDialog( main_window,
      gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
      type_map[type], buttons_map[buttons], msg )
    try:
      self.retval = response_map.get(d.run(), None)
      self.retval_valid = True
    finally:
      d.destroy()

  def result(self):
    while not self.retval_valid:
      time.sleep(.1)
    return self.retval


def info(msg, type='info', buttons='ok-cancel'):
  s = Show()
  do_gui_operation(s, msg, type, buttons)
  return s.result()

def warn(msg, buttons='ok-cancel'):
  return info(msg, 'warn', buttons)

def error(msg, buttons='ok-cancel'):
  return info(msg, 'error', buttons)

def ask(msg, buttons='yes-no'):
  return info(msg, 'ask', buttons)
