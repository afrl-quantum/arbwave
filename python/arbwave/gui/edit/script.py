# vim: ts=2:sw=2:tw=80:nowrap
"""Simple text editor for scripts.
This was mostly stolen from a demo from the pygtk project."""

import sys

from gi.repository import Gtk as gtk, Gdk as gdk

from ..packing import Args as PArgs, hpack, vpack, VBox

class Editor(gtk.Dialog):
  def __init__( self, title='Edit Script', parent=None, target=None,
                modal=False, notebook = None, keep_open=False):
    actions = \
      ([] if keep_open else [gtk.STOCK_SAVE,   gtk.ResponseType.OK]) + \
      [gtk.STOCK_APPLY,  gtk.ResponseType.APPLY] + \
      ([] if keep_open else [gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL])

    flags = gtk.DialogFlags.DESTROY_WITH_PARENT
    if modal:
      flags |= gtk.DialogFlags.MODAL
      actions.pop(2)
      actions.pop(2)

    super(Editor,self).__init__( title, parent, flags, tuple(actions) )
    self.notebook = notebook
    self.keep_open = keep_open

    # MECHANICS
    self.unset_changes()
    self.target = target



    self.set_default_size(550, 600)
    self.set_border_width(10)

    ## Create document
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    sw.set_shadow_type(gtk.ShadowType.IN)
    self.vbox.pack_start(sw, True, True, 0)

    self.contents = gtk.TextView()
    self.contents.grab_focus()
    sw.add(self.contents)

    ## Create statusbar
    self.statusbar = gtk.Label()
    self.action_area.pack_start(self.statusbar, True, True, 0)
    self.action_area.reorder_child(self.statusbar, 0)

    ## Show text widget info in the statusbar */
    self.buf = self.contents.get_buffer()
    if self.target:
      self.set_text( self.target.get_text() )

    self.buf.connect_object("changed", self.buffer_changed_callback, None)
    # cursor moved
    self.buf.connect_object("mark_set", self.mark_set_callback, None)
    self.connect('response', self.respond)

    self.update_statusbar()

    self.present()

  def _present_prep(self):
    if self.notebook and self.notebook.page_num(self.vbox) < 0:
      self.vbox.orig_parent = self
      if self.vbox in self.get_children():
        self.remove( self.vbox )
      button = gtk.Button('x')
      button.set_focus_on_click(False)
      button.connect('clicked', self.respond, gtk.ResponseType.CANCEL)
      self.notebook.append_page(
        self.vbox,
        hpack(gtk.Label(self.get_property('title')),
              button, border=0, show_all=True)
      )
      self.notebook.set_tab_reorderable(self.vbox, True)
      self.notebook.set_tab_detachable(self.vbox, True)
      if self.keep_open:
        button.hide()

    self.vbox.show_all()


  def present(self):
    self._present_prep()
    if self.notebook:
      self.vbox.show()
      self.notebook.set_current_page( self.notebook.page_num(self.vbox) )
    else:
      gtk.Dialog.present(self)


  def update_statusbar(self, other=''):
    iter = self.buf.get_iter_at_mark(self.buf.get_insert())

    row = iter.get_line()
    col = iter.get_line_offset()

    msg = "%d, %d%s %s" % \
      (row, col, (self.file_changed and " - Modified" or ""), other )

    self.statusbar.set_text(msg)

  def get_text(self):
    start, end = self.buf.get_bounds()
    return self.buf.get_text(start, end, False)

  def unset_changes(self):
    self.file_changed = False
    self.set_response_sensitive(gtk.ResponseType.OK, False)
    self.set_response_sensitive(gtk.ResponseType.APPLY, False)


  def set_changes(self):
    self.file_changed = True
    self.set_response_sensitive(gtk.ResponseType.OK, True)
    self.set_response_sensitive(gtk.ResponseType.APPLY, True)

  def set_text(self,text):
    self.buf.set_text(text)
    self.unset_changes()
    self.update_statusbar()

  def buffer_changed_callback(self,buf):
    self.set_changes()
    self.update_statusbar()


  def mark_set_callback(self, buf, new_location, mark):
    self.update_statusbar()


  def respond(self, dialog, response_id):
    if response_id in [gtk.ResponseType.OK, gtk.ResponseType.APPLY] and self.target:
      try:
        self.target.set_text( self.get_text(), from_editor=True )
        self.unset_changes()
        self.update_statusbar()
        self.contents.grab_focus()

      except Exception as e:
        # It looks like the target rejected our text...
        self.update_statusbar('  Could not save text!!!!')
        print(e)
        return

    if response_id in [gtk.ResponseType.OK, gtk.ResponseType.CANCEL] and self.target:
      # hide both to account for either notebook or dialog view
      self.vbox.hide()
      self.hide()
      self.set_text( self.target.get_text() )


def edit(title='Edit Script', parent=None, text=''):
  ed = Editor( title=title, parent=parent, modal=True )
  if text:
    ed.set_text(text)
  try:
    if ed.run() in [ gtk.ResponseType.OK, gtk.ResponseType.APPLY ]:
      return True, ed.get_text()
    else:
      return False, text
  finally:
    ed.destroy()


def main(argv):
  text='\n'.join(argv[1:])
  res = edit(text=text)
  print(res[0] == gtk.ResponseType.OK)
  print(res[1])

if __name__ == '__main__':
  sys.exit(main(sys.argv))

