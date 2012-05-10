# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import os, argparse, gtk, gobject, time, sys
import version, gui
from processor.default import get_globals

def sleeper():
  time.sleep(0.001)
  return 1 # necessary to ensure timeout is not removed

def main():
  parser = argparse.ArgumentParser(prog=version.prefix())
  parser.add_argument( '--version', action='version',
    version='%(prog)s '+version.version() )
  parser.add_argument('filename', nargs='?', help='configuration file')
  args = parser.parse_args()

  # this is necessary to ensure that threads can be launched!!!!
  gobject.threads_init()

  if sys.platform == 'win32':
    gtk.timeout_add(400, sleeper)

  prog = gui.ArbWave()
  if args.filename:
    assert os.path.isfile( args.filename ), 'expected configuration filename'
    prog.config_file = args.filename
    F = open( args.filename )
    prog.setvars( gui.storage.var_tools.readvars(F, get_globals()) )
    F.close()

  gtk.main()

