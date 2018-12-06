# vim: ts=2:sw=2:tw=80:nowrap
from gi.repository import Gtk as gtk, Gdk as gdk
import sys
from .helpers import *
from .spreadsheet import keys

class Dragger(object):
  def __init__(self, V, ui):
    self.ui = ui
    self.drop_started = False
    V.connect('drag-motion', self.drag_motion)
    V.connect('drag-data-received', self.drag_data_received)
    V.connect('drag-drop', self.drag_drop)
    V.connect('drag-begin', self.drag_begin)
    V.connect('drag-end', self.drag_end)
    self.model = None

  def drag_motion(self, w, ctx, x, y, time):
    gdk.drag_status(ctx, gdk.DragAction.COPY, time)

  def drag_data_received(self, w, ctx, x, y, seldata, info, time):
    if self.drop_started:
      ok, self.model, path = gtk.tree_get_row_drag_data(seldata)
      if not ok:
        raise RuntimeError('could not get tree drag data!')
      self.drop_info = w.get_dest_row_at_pos(x, y)

  def drag_begin(self, w, ctx):
    # pause updates because of waveform updates
    self.ui.pause()
    self.drop_started = False

  def drag_drop(self, w,ctx,x,y,time):
    self.drop_started = True

  def drag_end(self, w, ctx):
    if self.drop_started and ctx.get_selected_action() & gdk.DragAction.COPY:
      model = self.model
      path = -1
      if self.drop_info:
        path, position_ignore = self.drop_info

      new_label = model[ path ][model.LABEL] + '-copy-'
      all_labels = [ l[model.LABEL] for l in model ]
      for i in range(sys.maxsize):
        if new_label + str(i) not in all_labels:
          break

      model[path][model.LABEL] = new_label + str(i)
      model[path][model.WAVEFORMS] = model[path][model.WAVEFORMS].copy()

    self.drop_started = False
    # unpause updates, no need to trigger update unless waveform changes
    self.ui.unpause()

class Editor(object):
  def __init__(self, waveforms_set, ui, add_undo=None):
    self.waveforms_set = waveforms_set
    self.add_undo = add_undo
    self.ui = ui
    ws = waveforms_set

    V = self.view = gtk.TreeView( ws )
    V.set_reorderable(True)
    self.drag_response = Dragger( V, ui )
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
      lambda tv, c, m, i, u: c.set_property('text', repr(m[i][ ws.WAVEFORMS])))

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
      rows = [ gtk.TreeRowReference.new(model, p)  for p in rows ]
      for r in rows:
        model.remove( model.get_iter( r.get_path() ) )
      return True
    return False


class Dialog(gtk.Dialog):
  def __init__(self, waveforms_set,
               title='Waveform Set Editor', parent=None, add_undo=None):
    actions = [
      gtk.STOCK_OK,     gtk.ResponseType.OK,
      gtk.STOCK_APPLY,  gtk.ResponseType.APPLY,
      gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
    ]

    flags = gtk.DialogFlags.DESTROY_WITH_PARENT
    super(Dialog,self).__init__( title, parent, flags, tuple(actions) )

    self.set_default_size(300, 200)
    self.set_border_width(10)
    self.editor = Editor( waveforms_set, ui=parent, add_undo=add_undo )
    self.vbox.pack_start( self.editor.view, True, True, 0 )
    self.connect('response', self.respond)
    self.editor.view.get_selection() \
        .select_iter( waveforms_set.get_current_iter() )


  def respond(self, dialog, response_id):
    if response_id in [gtk.ResponseType.OK, gtk.ResponseType.APPLY]:
      model, iter = self.editor.view.get_selection().get_selected()
      if iter:
        model.set_current( model[iter][model.LABEL] )

    if response_id in [gtk.ResponseType.OK, gtk.ResponseType.CANCEL]:
      self.destroy()
