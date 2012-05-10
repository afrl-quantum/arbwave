# vim: ts=2:sw=2:tw=80:nowrap

import gtk
import os

from var_tools import *

current_dir = '~'

def get_file(doopen=True):
  info = {
    True : { 'action':gtk.FILE_CHOOSER_ACTION_OPEN, 'stock':gtk.STOCK_OPEN },
   False : { 'action':gtk.FILE_CHOOSER_ACTION_SAVE, 'stock':gtk.STOCK_SAVE },
  }
  filename = None
  chooser = gtk.FileChooserDialog(
    title='Choose file',
    action=info[doopen]['action'],
    buttons=( gtk.STOCK_CANCEL,
              gtk.RESPONSE_CANCEL,
              info[doopen]['stock'],
              gtk.RESPONSE_OK )
  )
  for p, n in [ ('*.py', 'Python Files') ]:
    filter = gtk.FileFilter()
    filter.add_pattern(p)
    filter.set_name(n)
    chooser.add_filter(filter)

  global current_dir
  folder = os.path.expanduser( current_dir )
  chooser.set_current_folder(folder)
  response = chooser.run()
  if response == gtk.RESPONSE_OK:
    filename = chooser.get_filename()
    current_dir = os.path.dirname( filename )
    chooser.destroy()
  elif response == gtk.RESPONSE_CANCEL:
    chooser.destroy()
  return filename

def gtk_open_handler(action, stor, globals=globals(), **locals):
  try:
    stor.config_file = get_file()
    F = open( stor.config_file )
  except TypeError:
    return # this happens when get_file returns None
  V = readvars( F, globals, **locals )
  F.close()
  stor.setvars( V )

def gtk_save_handler(action, stor, force_new=False):
  try:
    if (not force_new) and 'config_file' in dir(stor) and stor.config_file:
      F = open( stor.config_file, 'w' )
    else:
      stor.config_file = get_file(False)
      F = open( stor.config_file, 'w' )
  except TypeError:
    return # this happens when get_file returns None
  writevars( F, stor.getvars() )
  F.close()

