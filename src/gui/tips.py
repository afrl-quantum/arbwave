# vim: ts=2:sw=2:tw=80:nowrap

import gtk, pydoc
from ..processor import functions


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

