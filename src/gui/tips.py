# vim: ts=2:sw=2:tw=80:nowrap

import gtk, pydoc
from ..processor import functions
from ..processor.engine import Arbwave


def show_generators(parent):
  dialog = gtk.Dialog( 'Value Generators',
    parent, gtk.DIALOG_DESTROY_WITH_PARENT,
    (gtk.STOCK_CLOSE, gtk.RESPONSE_OK) )

  L = gtk.Label()
  scroll = gtk.ScrolledWindow()
  scroll.set_size_request(550,400)
  scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)

  scroll.add_with_viewport( L )
  dialog.vbox.pack_start( scroll )
  dialog.show_all()

  td = pydoc.TextDoc()

  text = list()
  for f in functions.registered.items():
    s = td.docroutine(f[1].__init__)
    text.append( '<b>{f}</b>:  {doc}' \
      .format(f=f[0],doc=s[ (s.find('method')+6): ] ))

  text = '\n'.join(text)
  L.set_markup( text )

  # Close dialog on user response
  dialog.connect ("response", lambda d, r: d.destroy())
  dialog.show()


def show_arbwavefunctions(parent):
  dialog = gtk.Dialog( 'Arbwave functions',
    parent, gtk.DIALOG_DESTROY_WITH_PARENT,
    (gtk.STOCK_CLOSE, gtk.RESPONSE_OK) )

  L = gtk.Label()
  scroll = gtk.ScrolledWindow()
  scroll.set_size_request(550,400)
  scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)

  scroll.add_with_viewport( L )
  dialog.vbox.pack_start( scroll )
  dialog.show_all()

  td = pydoc.TextDoc()

  text = list()
  for f in [
    ('arbwave.add_runnable',  Arbwave.add_runnable),
    ('arbwave.update',        Arbwave.update),
    ('arbwave.update_static', Arbwave.update_static),
    ('arbwave.update_plotter',Arbwave.update_plotter),
    ('arbwave.stop_check',    Arbwave.stop_check),
    ('arbwave.save_gnuplot',  Arbwave.save_gnuplot),
    ('arbwave.find',          Arbwave.find),
    ('arbwave.find_group',    Arbwave.find_group),
    ('arbwave.find_channel',  Arbwave.find_channel),
  ]:
    s = td.docroutine(f[1]).split('\n')
    args = s[0][ s[0].find('(') : (1 + s[0].find(')')) ]
    text.append(
      '\n'.join( ['<b>{f}{args}</b>'.format(f=f[0],args=args)] + s[1:] )
    )

  text = '\n'.join(text)
  L.set_markup( text )

  # Close dialog on user response
  dialog.connect ("response", lambda d, r: d.destroy())
  dialog.show()

