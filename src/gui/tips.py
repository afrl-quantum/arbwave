# vim: ts=2:sw=2:tw=80:nowrap

import gtk, pydoc
from ..processor import functions
from ..processor.engine import Arbwave


def show_generators(parent):
  dialog = gtk.MessageDialog(
    parent, gtk.DIALOG_DESTROY_WITH_PARENT,
    gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE )

  td = pydoc.TextDoc()

  text = list()
  for f in functions.registered.items():
    s = td.docroutine(f[1].__init__)
    text.append( '<b>{f}</b>:  {doc}' \
      .format(f=f[0],doc=s[ (s.find('method')+6): ] ))

  text = '\n'.join(text)
  dialog.set_markup( text )

  # Close dialog on user response
  dialog.connect ("response", lambda d, r: d.destroy())
  dialog.show()


def show_arbwavefunctions(parent):
  dialog = gtk.MessageDialog(
    parent, gtk.DIALOG_DESTROY_WITH_PARENT,
    gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE )

  td = pydoc.TextDoc()

  text = list()
  for f in [
    ('arbwave.add_runnable',  Arbwave.add_runnable),
    ('arbwave.update',        Arbwave.update),
    ('arbwave.update_static', Arbwave.update_static),
    ('arbwave.update_plotter',Arbwave.update_plotter),
    ('arbwave.stop_check',    Arbwave.stop_check),
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
  dialog.set_markup( text )

  # Close dialog on user response
  dialog.connect ("response", lambda d, r: d.destroy())
  dialog.show()

