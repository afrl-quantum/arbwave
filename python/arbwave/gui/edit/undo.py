# vim: ts=2:sw=2:tw=80:nowrap
"""
Simple text editor for undo/redo items.
"""

import sys

from gi.repository import Gtk as gtk

from .helpers import *
from ..packing import Args as PArgs, hpack, vpack, VBox

def get_undo_cell_text(tv, c, m, i, u):
  c.set_property('text', str(m[i][0]))

class Undo(gtk.Dialog):
  def __init__(self, title, parent, target):
    actions = [gtk.STOCK_CLOSE, gtk.ResponseType.CLOSE]

    flags = gtk.DialogFlags.DESTROY_WITH_PARENT

    super(Undo,self).__init__( title, parent, flags, tuple(actions) )

    self.target = target

    self.set_default_size(0, 200)
    self.set_border_width(10)

    # scrolled window for undo
    R = GCRT()
    C = GTVC('Undo Items', R)
    C.set_cell_data_func(R, get_undo_cell_text)
    self.undo_view = gtk.TreeView(target._undo)
    self.undo_view.append_column( C )
    undo_sw = gtk.ScrolledWindow()
    undo_sw.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    undo_sw.set_shadow_type(gtk.ShadowType.IN)
    undo_sw.add(self.undo_view)

    # scrolled window for redo
    R = GCRT()
    C = GTVC('Redo Items', R)
    C.set_cell_data_func(R, get_undo_cell_text)
    self.redo_view = gtk.TreeView(target._redo)
    self.redo_view.append_column( C )
    redo_sw = gtk.ScrolledWindow()
    redo_sw.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    redo_sw.set_shadow_type(gtk.ShadowType.IN)
    redo_sw.add(self.redo_view)

    # construct layout
    self.vbox.pack_start(hpack(undo_sw, redo_sw), True, True, 0)

    # Undo/Redo Buttons
    ub = gtk.Button(label='Undo')
    rb = gtk.Button(label='Redo')
    cb = gtk.Button(label='Clear')
    ub.connect('clicked', lambda *a: self.target.undo())
    rb.connect('clicked', lambda *a: self.target.redo())
    cb.connect('clicked', lambda *a: self.target.clear())

    ## Add undo/redo/clear buttons to action area
    self.action_area.pack_start(ub, True, True, 0)
    self.action_area.pack_start(rb, True, True, 0)
    self.action_area.pack_start(cb, True, True, 0)
    self.action_area.reorder_child(ub, 0)
    self.action_area.reorder_child(rb, 1)
    self.action_area.reorder_child(cb, 2)

    self.connect('response', self.respond)

    self.present()

  def present(self):
    self.vbox.show_all()
    super(Undo,self).present()

  def respond(self, dialog, response_id):
    if response_id in [gtk.ResponseType.CLOSE]:
      # hide both to account for either notebook or dialog view
      self.hide()
