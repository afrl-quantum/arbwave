# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import os, argparse, gtk, gobject, time, sys, logging, threading
import version
import options
from tools.gui_callbacks import do_gui_operation

log_levels = {
  'ALL'   : 0,
  'DEBUG' : logging.DEBUG,
  'INFO'  : logging.INFO,
  'WARN'  : logging.WARN,
  'ERROR' : logging.ERROR,
  'FATAL' : logging.FATAL,
}

def sleeper():
  time.sleep(0.001)
  return 1 # necessary to ensure timeout is not removed

def main():
  parser = argparse.ArgumentParser(prog=version.prefix())
  parser.add_argument( '--version', action='version',
    version='%(prog)s '+version.version() )
  parser.add_argument( 'filename', nargs='?', help='configuration file' )
  parser.add_argument( '--simulated', action='store_true',
    help='Use simulated hardware' )
  parser.add_argument( '--log-level', choices=log_levels, default='INFO' )
  args = parser.parse_args()

  options.simulated = args.simulated
  logging.root.setLevel( log_levels[ args.log_level ] )

  # this is necessary to ensure that threads can be launched!!!!
  gobject.threads_init()

  if sys.platform == 'win32':
    gobject.timeout_add(400, sleeper)


  # we have to do these imports _after_ the options. module is modified
  import gui
  from processor.default import get_globals
  prog = gui.ArbWave()
  if args.filename:
    assert os.path.isfile( args.filename ), 'expected configuration filename'
    def load_file():
      try:
        gui.storage.load_file( args.filename, prog, get_globals() )
      except Exception, e:
        do_gui_operation( prog.notify.show, str(e) )

    # This has to be done in a separate thread so that all gui notifications are
    # handled in the gui
    t = threading.Thread( target=load_file )
    t.daemon = True # exit if the main thread has exited
    t.start()

  gtk.main()

