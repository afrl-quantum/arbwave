# vim: et:ts=2:sw=2:tw=80:nowrap
#
#       Py_Shell.py : inserts the python prompt in a gtk interface
#

try:
  from .. import options
  if not options.ipython:
    raise
  import IPython
  assert IPython.version_info <= (2,0,0,''), ''

  from .embedded_ipython import Python
except:
  from .old_embedded import Python

if __name__ == "__main__":
  from gi.repository import Gtk as gtk
  window = gtk.Window()
  window.set_default_size(640, 320)
  window.connect('delete-event', lambda x, y: gtk.main_quit())
  sb = gtk.ScrolledWindow()
  sb.add(Python())
  window.add( sb )
  window.show_all()
  gtk.main()
