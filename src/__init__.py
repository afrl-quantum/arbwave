# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import os, argparse, gtk, gobject, time, sys, logging
import version
import options

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
    gtk.timeout_add(400, sleeper)


  # we have to do these imports _after_ the options. module is modified
  import gui
  from processor.default import get_globals
  prog = gui.ArbWave()
  if args.filename:
    assert os.path.isfile( args.filename ), 'expected configuration filename'
    prog.config_file = args.filename
    F = open( args.filename )
    prog.setvars( gui.storage.var_tools.readvars(F, get_globals()) )
    F.close()

  gtk.main()

