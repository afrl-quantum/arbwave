# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk

default_boxpack = {
  'spacing' : 1,
  'border'  : 2,
  'show_all': False,
}
class Args:
  def __init__(self, item, expand=True,fill=True,padding=0):
    self.args = (item, expand, fill, padding)

def hpack(*items, **kwargs):
  args = default_boxpack
  args.update( kwargs )
  hbox = gtk.HBox(spacing=args['spacing'])
  hbox.set_border_width(args['border'])
  for i in items:
    if i.__class__ is Args:
      hbox.pack_start(*i.args)
    else:
      hbox.pack_start(i, True, True, 0)
  if args['show_all']:
    hbox.show_all()
  return hbox


def vpack(*items, **kwargs):
  args = default_boxpack
  args.update( kwargs )
  vbox = gtk.VBox(spacing=args['spacing'])
  vbox.set_border_width(args['border'])
  for i in items:
    if i.__class__ is Args:
      vbox.pack_start(*i.args)
    else:
      vbox.pack_start(i, True, True, 0)
  return vbox


def VBox(**kwargs):
  args = default_boxpack
  args.update( kwargs )
  vbox = gtk.VBox(spacing=args['spacing'])
  vbox.set_border_width( args['border'] )
  return vbox

