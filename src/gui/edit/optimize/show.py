# vim: ts=2:sw=2:tw=80:nowrap

import gtk

from ..helpers import GTVC

class Show(gtk.Dialog):
  def __init__(self, columns, title='Optimization Parameters',
               parent=None, target=None, model=False):
    actions = [
    #  gtk.STOCK_OK,     gtk.RESPONSE_OK,
    #  gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL
    ]
    flags = gtk.DIALOG_DESTROY_WITH_PARENT
    gtk.Dialog.__init__( self, title, parent, flags, tuple(actions) )

    self.set_default_size(550, 600)
    self.set_border_width(10)

    self.params = gtk.ListStore( *([str]*(len(columns))) )
    V = gtk.TreeView( self.params )
    resultCell = gtk.CellRendererText()
    for i in xrange(len(columns)):
      V.append_column( GTVC(columns[i], gtk.CellRendererText(), text=i) )
    V.show()
    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,-1)
    scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    scroll.add( V )
    scroll.show()
    self.vbox.pack_start(scroll)

  def add(self, *stuff):
    self.params.append( stuff )


