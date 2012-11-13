# vim: ts=2:sw=2:tw=80:nowrap

import gtk
import os

from var_tools import *

current_dir = '~'

class NoFileError(Exception):
  pass

def get_file(doopen=True, filters=[('*.py', 'Python Files')]):
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
  for p, n in filters:
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
  elif response == gtk.RESPONSE_CANCEL:
    pass

  chooser.destroy()
  if filename is None:
    raise NoFileError()

  current_dir = os.path.dirname( filename )
  return filename


def load_file( filename, stor, globals=globals(), **locals ):
  F = open( filename )
  V = readvars( F, globals, **locals )
  F.close()
  stor.clearvars()
  stor.set_config_file( filename )
  stor.setvars( V )
  stor.set_file_saved()


def gtk_open_handler(action, stor, globals=globals(), **locals):
  try:
    config_file = get_file()
    F = open( config_file )
    load_file( config_file, stor, globals, **locals )
  except NoFileError:
    return # this happens when get_file returns None

def gtk_save_handler(action, stor, force_new=False):
  try:
    config_file = stor.get_config_file()
    if (not force_new) and config_file:
      F = open( config_file, 'w' )
    else:
      config_file = get_file(False)
      F = open( config_file, 'w' )
      stor.set_config_file( config_file )
  except NoFileError:
    return # this happens when get_file returns None
  writevars( F, stor.getvars() )
  stor.set_file_saved()
  F.close()

