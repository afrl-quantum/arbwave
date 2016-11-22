# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk
import pydoc
from ..processor import functions


def show_autovars(parent):
  dialog = gtk.Dialog( 'Automatically Generated Local Waveform Variables',
    parent, gtk.DialogFlags.DESTROY_WITH_PARENT,
    (gtk.STOCK_CLOSE, gtk.ResponseType.OK) )

  L = gtk.Label()
  scroll = gtk.ScrolledWindow()
  scroll.set_size_request(550,400)
  scroll.set_shadow_type(gtk.ShadowType.ETCHED_IN)

  scroll.add_with_viewport( L )
  dialog.vbox.pack_start( scroll, True, True, 0 )
  dialog.show_all()

  L.set_markup("""\
Arbwave develops the complete timing diagram of a waveform using a concept known
known as <i>Natural Time</i>.
<i>Natural Time</i> is defined as the time that a waveform group or element
begins based upon the preceding sibling groups or preceding waveform elements
of the same Arbwave channel.
In order to make the use of natural time more convenient, Arbwave automatically
generates and provides the following variables:
  <b>t</b>: Local time (units: time)
  <b>dt</b>: Duration of parent group (units: time)
  <b>dt_clk</b>: Minimum clock period of a waveform element (units: time)
  """)

  # Close dialog on user response
  dialog.connect ("response", lambda d, r: d.destroy())
  dialog.show()


def show_generators(parent):
  dialog = gtk.Dialog( 'Value Generators',
    parent, gtk.DialogFlags.DESTROY_WITH_PARENT,
    (gtk.STOCK_CLOSE, gtk.ResponseType.OK) )

  L = gtk.Label()
  scroll = gtk.ScrolledWindow()
  scroll.set_size_request(550,400)
  scroll.set_shadow_type(gtk.ShadowType.ETCHED_IN)

  scroll.add_with_viewport( L )
  dialog.vbox.pack_start( scroll, True, True, 0 )
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
  from ..processor.engine import Arbwave
  dialog = gtk.Dialog( 'Arbwave functions',
    parent, gtk.DialogFlags.DESTROY_WITH_PARENT,
    (gtk.STOCK_CLOSE, gtk.ResponseType.OK) )

  L = gtk.Label()
  scroll = gtk.ScrolledWindow()
  scroll.set_size_request(550,400)
  scroll.set_shadow_type(gtk.ShadowType.ETCHED_IN)

  scroll.add_with_viewport( L )
  dialog.vbox.pack_start( scroll, True, True, 0 )
  dialog.show_all()

  td = pydoc.TextDoc()

  text = list()
  for f in [
    ('Arbwave.add_runnable',  Arbwave.add_runnable),
    ('Arbwave.update',        Arbwave.update),
    ('Arbwave.update_static', Arbwave.update_static),
    ('Arbwave.update_plotter',Arbwave.update_plotter),
    ('Arbwave.stop_check',    Arbwave.stop_check),
    ('Arbwave.save_gnuplot',  Arbwave.save_gnuplot),
    ('Arbwave.find',          Arbwave.find),
    ('Arbwave.find_group',    Arbwave.find_group),
    ('Arbwave.find_channel',  Arbwave.find_channel),
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

