# vim: ts=2:sw=2:tw=80:nowrap
"""
This package is responsible for the logic that converts waveforms descriptions
to more explicit channel-specific full waveforms.
"""

from gi.repository import GLib as glib

def do_gui_operation(fun, *args, **kwargs):
  def idle_fun():
    fun(*args, **kwargs)
    return False

  glib.idle_add(idle_fun)


def do_later(time, fun, *args, **kwargs):
  def idle_fun():
    fun(*args, **kwargs)
    return False

  glib.timeout_add(time,idle_fun)
