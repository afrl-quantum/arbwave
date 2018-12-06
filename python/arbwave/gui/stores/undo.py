# vim: ts=2:sw=2:tw=80:nowrap
"""
Somewhat lightweight storage for undo/redo stacks and an editor to show/clear
these stacks.
"""

from gi.repository import Gtk as gtk
from logging import log, DEBUG

from .. import edit

class Base(object):
  """Base Undo class (this one raises exceptions)"""
  name = 'Null edit'
  def __str__(self):
    return self.name

  def undo(self):
    raise NotImplementedError('undo should be implemented properly')

  def redo(self):
    raise NotImplementedError('redo should be implemented properly')

def pop_liststore(L):
  if len(L) == 0:
    raise IndexError('Cannot pop item from empty stack')
  i = L.get_iter(len(L)-1)
  obj = L[i][0]
  L.remove(i)
  del i
  return obj


class Undo(object):
  def __init__(self, title='Undo/Redo List', parent=None, changed=None):
    self.editor   = None
    self.title    = title
    self.parent   = parent

    self._undo = gtk.ListStore.new((object,))
    self._redo = gtk.ListStore.new((object,))

    # index of the last undo item that successfully updated hardware and plots
    self.last_good_idx = -1

    self.changed        = changed

  def clear(self):
    log(DEBUG-1,'undo/redo.clear....')
    self._undo.clear()  # remove all current undo items
    self._redo.clear()  # remove all current undo items
    self.last_good_idx = -1

  def mark_good(self):
    self.last_good_idx = len(self._undo) - 1

  @property
  def number_failed(self):
    return (len(self._undo) -1) - self.last_good_idx

  def add(self, item):
    self._undo.append( [item] )
    self._redo.clear() # remove all current redo items
    if self.changed:
      self.changed()

  def undo(self):
    try:
      change = pop_liststore(self._undo)
      log(DEBUG-1,'undo last operation')
      change.undo()
      self._redo.append( [change] )
    except IndexError:
      pass

  def redo(self):
    try:
      change = pop_liststore(self._redo)
      log(DEBUG-1,'redo last undone operation')
      change.redo()
      self._undo.append( [change] )
    except IndexError:
      pass



  def show(self):

    def unset_editor(*args):
      self.editor = None

    if not self.editor:
      self.editor = edit.Undo(self.title, self.parent, target=self)
      self.editor.connect('delete-event', lambda *a:self.editor.hide_on_delete())
      self.editor.connect('destroy', unset_editor)

    self.editor.present()
