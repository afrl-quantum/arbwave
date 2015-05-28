# vim: ts=2:sw=2:tw=80:nowrap
import gtk, sys
from helpers import *
from spreadsheet import keys

class Dragger(object):
  def __init__(self, V):
    self.drop_started = False
    V.connect('drag-motion', self.drag_motion)
    V.connect('drag-data-received', self.drag_data_received)
    V.connect('drag-drop', self.drag_drop)
    V.connect('drag-begin', self.drag_begin)
    V.connect('drag-end', self.drag_end)
    self.model = None

  def drag_motion(self, w, ctx, x, y, time):
    mask = w.window.get_pointer()[2]
    if mask & gtk.gdk.CONTROL_MASK:
      ctx.drag_status( gtk.gdk.ACTION_COPY, time )

  def drag_data_received(self, w, ctx, x, y, seldata, info, time):
    if self.drop_started and ctx.action & gtk.gdk.ACTION_COPY:
      model, path = seldata.tree_get_row_drag_data()
      new_label = model[ path ][model.LABEL] + '-copy-'
      all_labels = [ l[model.LABEL] for l in model ]
      for i in xrange(sys.maxint):
        if new_label + str(i) not in all_labels:
          break
      # now make a new row that gets moved
      # FIXME
      model.append(
        (new_label + str(i), model[path][model.WAVEFORMS].copy()) )
      seldata.tree_set_row_drag_data(model, model[-1].path)
      self.model = model
      return False

  def drag_begin(self, w, ctx):
    self.drop_started = False

  def drag_drop(self, w,ctx,x,y,time):
    self.drop_started = True

  def drag_end(self, w, ctx):
    if ctx.action & gtk.gdk.ACTION_COPY:
      # clean  up!
      del self.model[-1]

class Editor(object):
  def __init__(self, waveforms_set, add_undo=None):
    self.add_undo = add_undo
    self.waveforms_set = waveforms_set
    ws = waveforms_set

    V = self.view = gtk.TreeView( ws )
    V.set_reorderable(True)
    self.drag_response = Dragger( V )
    V.connect('key-press-event', self.view_keypress_cb)
    R = {
      'label'   : GCRT(),
      'waveform': GCRT(),
    }

    R['label'   ].set_property( 'editable', True )
    R['waveform'].set_property( 'editable', False )
    R['label'].connect( 'edited', set_item, ws, ws.LABEL, self.add_undo, True )

    C = {
      'label'   : GTVC( 'Label',    R['label'   ],text=ws.LABEL ),
      'waveform': GTVC( 'Waveform', R['waveform'],text=ws.WAVEFORMS ),
    }

    C['waveform'].set_cell_data_func( R['waveform'],
      lambda tv, c, m, i: c.set_property('text', repr(m[i][ ws.WAVEFORMS])))

    V.append_column( C['label'] )
    V.append_column( C['waveform'] )
    V.show_all()


  def view_keypress_cb(self, entry, event):
    if event.keyval == keys.INSERT:
      model, rows = self.view.get_selection().get_selected_rows()
      # we convert paths to row references so that references are persistent
      if rows:
        rows = [ model.get_iter(p)  for p in rows ]
        for row in rows:
          p = model[row].parent and model[row].parent.iter
          model.insert_before( row, self.waveforms_set.get_default() )
      else:
        model.append( self.waveforms_set.get_default() )
      return True
    elif event.keyval == keys.DEL:
      model, rows = self.view.get_selection().get_selected_rows()
      # we convert paths to row references so that references are persistent
      rows = [ gtk.TreeRowReference(model, p)  for p in rows ]
      for r in rows:
        model.remove( model.get_iter( r.get_path() ) )
      return True
    return False


class Dialog(gtk.Dialog):
  def __init__(self, waveforms_set, dialog=False,
               title='Waveform Set Editor', parent=None, add_undo=None):
    if dialog:
      actions = [
        gtk.STOCK_OK,     gtk.RESPONSE_OK,
        gtk.STOCK_APPLY,  gtk.RESPONSE_APPLY,
        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
      ]

    else:
      actions = []
    flags = gtk.DIALOG_DESTROY_WITH_PARENT
    gtk.Dialog.__init__( self, title, parent, flags, tuple(actions) )

    self.set_default_size(300, 200)
    self.set_border_width(10)
    self.editor = Editor( waveforms_set, add_undo=add_undo )
    self.vbox.pack_start( self.editor.view )
    if dialog:
      self.connect('response', self.respond)
      self.editor.view.get_selection() \
          .select_iter( waveforms_set.get_current_iter() )


  def respond(self, dialog, response_id):
    if response_id in [gtk.RESPONSE_OK, gtk.RESPONSE_APPLY]:
      model, iter = self.editor.view.get_selection().get_selected()
      if iter:
        model.set_current( model[iter][model.LABEL] )

    if response_id in [gtk.RESPONSE_OK, gtk.RESPONSE_CANCEL]:
      self.destroy()
