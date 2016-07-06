# vim: ts=2:sw=2:tw=80:nowrap
"""
GUI main

This import is supposed _after_ the options. module is modified
"""

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk as gtk, GLib as glib
import os, time, sys, logging, threading
from .tools.gui_callbacks import do_gui_operation

def sleeper():
  time.sleep(0.001)
  return 1 # necessary to ensure timeout is not removed

def main(args):
  if sys.platform == 'win32':
    glib.timeout_add(400, sleeper)

  import gui
  from processor.default import get_globals
  prog = gui.ArbWave()
  if args.filename:
    assert os.path.isfile( args.filename ), 'expected configuration filename'
    def load_file():
      try:
        logging.debug('Trying to load config file at startup...')
        gui.storage.load_file( args.filename, prog, get_globals() )
        logging.debug('Loaded config file at startup.')
      except Exception, e:
        do_gui_operation( prog.notify.show, str(e) )

    # This has to be done in a separate thread so that all gui notifications are
    # handled in the gui
    t = threading.Thread( target=load_file )
    t.daemon = True # exit if the main thread has exited
    t.start()

  # for whatever reason, there appears to be a race condition in setting up the
  # Gtk3 windows.  This small pause seems to work around this.
  time.sleep(.1)
  gtk.main()
