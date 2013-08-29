# vim: ts=2:sw=2:tw=80:nowrap

import gtk
import os, sys, traceback, logging

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
  F = open( filename )
  try:
    logging.debug('interpreting python in config file %s...', filename)
    V = readvars( F, globals, **locals )
    logging.debug('finished interpreting python in config file %s.', filename)
  except:
    raise LoadException( *sys.exc_info() )
  finally:
    F.close()
  logging.debug('stor.clearvars()...')
  stor.clearvars()
  logging.debug('stor.clearvars() finished.')
  stor.set_config_file( filename )
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
      stor.set_config_file( config_file )
  except NoFileError:
    return # this happens when get_file returns None
  writevars( F, stor.getvars() )
  stor.set_file_saved()
  F.close()

