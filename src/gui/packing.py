# vim: ts=2:sw=2:tw=80:nowrap

import gtk

default_boxpack = {
  'spacing' : 1,
  'border'  : 2,
}
class Args:
  def __init__(self,*args,**kwargs):
    self.args = args
    self.kwargs = kwargs

def hpack(*items, **kwargs):
  args = default_boxpack
  args.update( kwargs )
  hbox = gtk.HBox(spacing=args['spacing'])
  hbox.set_border_width(args['border'])
  for i in items:
    if i.__class__ is Args:
      hbox.pack_start(*i.args, **i.kwargs)
    else:
      hbox.pack_start(i)
  return hbox


def vpack(*items, **kwargs):
  args = default_boxpack
  args.update( kwargs )
  vbox = gtk.VBox(spacing=args['spacing'])
  vbox.set_border_width(args['border'])
  for i in items:
    if i.__class__ is Args:
      vbox.pack_start(*i.args, **i.kwargs)
    else:
      vbox.pack_start(i)
  return vbox


def VBox(**kwargs):
  args = default_boxpack
  args.update( kwargs )
  vbox = gtk.VBox(spacing=args['spacing'])
  vbox.set_border_width( args['border'] )
  return vbox

