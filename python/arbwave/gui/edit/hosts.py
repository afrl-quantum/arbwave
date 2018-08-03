# vim: ts=2:sw=2:tw=80:nowrap
from gi.repository import Gtk as gtk, Pango as pango
from .helpers import *

def create(hosts):
  editor = dict(
    view      = gtk.TreeView( hosts ),
    renderers = dict(
      prefix  = gtk.CellRendererText(),
      host    = gtk.CellRendererText(),
      default = gtk.CellRendererToggle(),
    ),
  )
  R = editor['renderers']

  #FIXME:  find some way to indicate that prefix is ignored for default host
  R['prefix' ].set_property( 'editable', True )
  R['host'   ].set_property( 'editable', True )
  R['default'].set_property( 'activatable', True )
  R['default'].set_property( 'radio', True )
  R['host'   ].set_property( 'alignment', pango.Alignment.CENTER )
  R['prefix' ].connect( 'edited', set_item, hosts, hosts.PREFIX )
  R['host'   ].connect( 'edited', set_item, hosts, hosts.HOST )
  R['default'].connect( 'toggled', select_radio_item, hosts, hosts.DEFAULT )

  editor.update(
    columns = dict(
      prefix  = GTVC( 'Prefix',   R['prefix'],  text=hosts.PREFIX ),
      host    = GTVC( 'Host',     R['host'],    text=hosts.HOST ),
      default = GTVC( 'Default?', R['default'] ),
    ),
  )

  C = editor['columns']
  V = editor['view']
  C['default'].add_attribute( R['default'], 'active', hosts.DEFAULT )

  #selection = V.get_selection()
  #selection.set_select_function(
  #  # Row selectable only if sensitive
  #  lambda path: not hosts[path][hosts.PROTECTED]
  #)

  #V.set_property( 'hover_selection', True )
  V.append_column( C['prefix'] )
  V.append_column( C['host'] )
  V.append_column( C['default'] )
  return editor
