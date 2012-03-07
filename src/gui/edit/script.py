# vim: ts=2:sw=2:tw=80:nowrap
"""Simple text editor for scripts.
This was mostly stolen from a demo from the pygtk project."""

import sys

import gtk

class Editor(gtk.Dialog):
  def __init__(self, title='Edit Script', parent=None, target=None):
    gtk.Dialog.__init__(self, title, parent,
      gtk.DIALOG_DESTROY_WITH_PARENT,
      (gtk.STOCK_SAVE, gtk.RESPONSE_OK,
       gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
       gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    )

    # MECHANICS
    self.unset_changes()
    self.target = target



    self.set_default_size(550, 600)
    self.set_border_width(10)

    table = gtk.Table(1, 3, False)
    self.vbox.pack_start(table)

    ## Create document 
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.set_shadow_type(gtk.SHADOW_IN)
    table.attach(sw,
		 # /* X direction */       /* Y direction */
                 0, 1,                   1, 2,
                 gtk.EXPAND | gtk.FILL,  gtk.EXPAND | gtk.FILL,
                 0,                      0)
  
    contents = gtk.TextView()
    contents.grab_focus()
    sw.add(contents)

    ## Create statusbar
  
    self.statusbar = gtk.Statusbar()
    table.attach(self.statusbar,
		 #/* X direction */       /* Y direction */
                 0, 1,                   2, 3,
                 gtk.EXPAND | gtk.FILL,  0,
                 0,                      0);
    
    ## Show text widget info in the statusbar */
    self.buf = contents.get_buffer()
    if self.target:
      self.set_text( self.target.get_text() )
  
    self.buf.connect_object("changed", self.buffer_changed_callback, None)
    # cursor moved
    self.buf.connect_object("mark_set", self.mark_set_callback, None)
    self.connect_object("window_state_event", self.update_resize_grip, 0)
    self.connect('response', self.respond)
  
    self.update_statusbar()
  
    self.show_all()



  def update_statusbar(self, other=''):
    self.statusbar.pop(0)
    
    iter = self.buf.get_iter_at_mark(self.buf.get_insert())
    
    row = iter.get_line()
    col = iter.get_line_offset()
    
    msg = "%d, %d%s %s" % \
      (row, col, (self.file_changed and " - Modified" or ""), other )
    
    self.statusbar.push(0, msg)

  def get_text(self):
    start, end = self.buf.get_bounds()
    return self.buf.get_text(start, end, False)

  def unset_changes(self):
    self.file_changed = False
    self.set_response_sensitive(gtk.RESPONSE_OK, False)
    self.set_response_sensitive(gtk.RESPONSE_APPLY, False)


  def set_changes(self):
    self.file_changed = True
    self.set_response_sensitive(gtk.RESPONSE_OK, True)
    self.set_response_sensitive(gtk.RESPONSE_APPLY, True)

  def set_text(self,text):
    self.buf.set_text(text)
    self.unset_changes()
    self.update_statusbar()

  def buffer_changed_callback(self,buf):
    self.set_changes()
    self.update_statusbar()


  def mark_set_callback(self, buf, new_location, mark):
    self.update_statusbar()

  def update_resize_grip(self, widget, event):
    if event.changed_mask & (gtk.gdk.WINDOW_STATE_MAXIMIZED | 
                             gtk.gdk.WINDOW_STATE_FULLSCREEN):
      maximized = event.new_window_state & (gtk.gdk.WINDOW_STATE_MAXIMIZED | 
                                            gtk.gdk.WINDOW_STATE_FULLSCREEN)
      self.statusbar.set_has_resize_grip(not maximized)


  def respond(self, dialog, response_id):
    if response_id in [gtk.RESPONSE_OK, gtk.RESPONSE_APPLY] and self.target:
      try:
        self.target.set_text( self.get_text() )
        self.unset_changes()
      except:
        # It looks like the target rejected our text...
        self.update_statusbar('  Could not save text!!!!')
        return

    if response_id in [gtk.RESPONSE_OK, gtk.RESPONSE_CANCEL]:
      self.hide()
      self.set_text( self.target.get_text() )


def edit(title='Edit Script', parent=None, text=''):
  ed = Editor( title=title, parent=parent )
  if text:
    ed.set_text(text)
  if ed.run() in [ gtk.RESPONSE_OK, gtk.RESPONSE_APPLY ]:
    return True, ed.get_text()
  else:
    return False, ''


def main(argv):
  text='\n'.join(argv[1:])
  res = edit(text=text)
  print res[0] == gtk.RESPONSE_OK
  print res[1]

if __name__ == '__main__':
  sys.exit(main(sys.argv))

