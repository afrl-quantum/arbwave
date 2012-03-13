# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import os, argparse, gtk
import version, gui

def main():
  parser = argparse.ArgumentParser(prog=version.prefix())
  parser.add_argument( '--version', action='version',
    version='%(prog)s '+version.version() )
  parser.add_argument('filename', nargs='?', help='configuration file')
  args = parser.parse_args()

  prog = gui.ArbWave()
  if args.filename:
    assert os.path.isfile( args.filename ), 'expected configuration filename'
    prog.config_file = args.filename
    F = open( args.filename )
    prog.setvars( gui.storage.var_tools.readvars(F) )
    F.close()

  gtk.main()

