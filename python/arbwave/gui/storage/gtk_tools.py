# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk
import os, sys, traceback, logging

from .var_tools import *

current_dir = '~'

class NoFileError(Exception):
  pass

def get_file(doopen=True, filters=[('*.py', 'Python Files')],
             default_dir=None, default_filename=None):
  info = {
    True : { 'action':gtk.FileChooserAction.OPEN, 'stock':gtk.STOCK_OPEN },
   False : { 'action':gtk.FileChooserAction.SAVE, 'stock':gtk.STOCK_SAVE },
  }
  filename = None
  chooser = gtk.FileChooserDialog(
    title='Choose file',
    action=info[doopen]['action'],
    buttons=( gtk.STOCK_CANCEL,
              gtk.ResponseType.CANCEL,
              info[doopen]['stock'],
              gtk.ResponseType.OK )
  )
  for p, n in filters:
    filter = gtk.FileFilter()
    filter.add_pattern(p)
    filter.set_name(n)
    chooser.add_filter(filter)

  global current_dir
  set_dir = default_dir
  if set_dir is None:
    set_dir = current_dir
  folder = os.path.expanduser( set_dir )
  chooser.set_current_folder(folder)
  if default_filename is not None:
    chooser.set_current_name(default_filename)
  response = chooser.run()
  if response == gtk.ResponseType.OK:
    filename = chooser.get_filename()
  elif response == gtk.ResponseType.CANCEL:
    pass

  chooser.destroy()
  if filename is None:
    raise NoFileError()

  if not default_dir:
    # only update the current directory when we are not given a spefic default
    # directdory
    current_dir = os.path.dirname( filename )
  return filename


class LoadException(Exception):
  def __init__( self, typ, value, tb ):
    Exception.__init__(self)

    if typ is SyntaxError:
      self.filename = value.filename
      self.lineno   = value.lineno
      self.line     = '<span font="monospace">'+value.text.rstrip()+'</span>'
      self.msg      = \
        '<span font="monospace">'+' '*(value.offset - 1) + '^</span>\n' \
        '   <span color="green">...</span>\n' \
        '<span color="red">SyntaxError: ' + value.msg + '</span>'

    else:
      self.filename = tb.tb_next.tb_next.tb_frame.f_code.co_filename
      self.lineno   = tb.tb_next.tb_next.tb_frame.f_lineno
      self.msg      = \
        '   <span color="green">...</span>\n' \
        '  <span color="red">' + str(value) + '</span>'

      f = open( self.filename )
      self.line = f.readlines()[self.lineno-1].rstrip()
      if len(self.line) > 40:
        self.line = self.line[:40] + '<span color="green">...</span>'


  def __str__(self):
    return \
      '<span color="red"><b>Error</b>:'   '\n' \
      '   Error loading configuration file:</span>\n' \
      '     <span color="orange"><i>{f}:{n}</i></span>'        '\n' \
      '   <span color="green">...</span>   \n' \
      '{l}'                               '\n' \
      '{m}'                               '\n' \
      .format( f=self.filename, n=self.lineno, l=self.line, m=self.msg )


def load_file( filename, stor, globals=globals(), **locals ):
  try:
    logging.debug('interpreting python in config file %s...', filename)
    V = readvars( filename, globals, **locals )
    logging.debug('finished interpreting python in config file %s.', filename)
  except:
    raise LoadException( *sys.exc_info() )
  logging.debug('stor.clearvars()...')
  stor.clearvars()
  logging.debug('stor.clearvars() finished.')
  stor.set_file_saved(False, filename)
  logging.debug('stor.setvars()...')
  stor.setvars( V )
  logging.debug('stor.setvars() finished.')
  stor.set_file_saved()


def gtk_open_handler(action, stor, globals=globals(), **locals):
  try:
    config_file = get_file()
    F = open( config_file )
    load_file( config_file, stor, globals, **locals )
  except NoFileError:
    pass # this happens when get_file returns None

def gtk_save_handler(action, stor, force_new=False):
  try:
    config_file = stor.get_config_file()
    if (not force_new) and config_file:
      F = open( config_file, 'w' )
    else:
      config_file = get_file(False)
      F = open( config_file, 'w' )
      stor.set_file_saved(None, config_file)
  except NoFileError:
    return # this happens when get_file returns None
  writevars( F, stor.getvars() )
  stor.set_file_saved()
  F.close()

