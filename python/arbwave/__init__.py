# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import sys, argparse, logging
from . import version, options, backend
from .runnable import Runnable

__all__ = [
  'version', 'options', 'backend', 'Runnable',
]

log_levels = {
  'ALL'   : 0,
  'DEBUG' : logging.DEBUG,
  'INFO'  : logging.INFO,
  'WARN'  : logging.WARN,
  'ERROR' : logging.ERROR,
  'FATAL' : logging.FATAL,
}

def main():
  if sys.platform != 'win32':
    # until we get a better multiprocessing with set_start_method (by a backport
    # or moving to python3), we need to use billiard on non-windows systems
    import billiard as mp
    mp.set_start_method('spawn')

  parser = argparse.ArgumentParser(prog=version.prefix())
  parser.add_argument( '--version', action='version',
    version='%(prog)s '+version.version() )
  parser.add_argument( 'filename', nargs='?', help='configuration file' )
  parser.add_argument( '--simulated', action='store_true',
    help='Use simulated hardware' )
  parser.add_argument( '--dataviewer', action='store_true',
    help='Start only the data viewer' )
  parser.add_argument( '--log-level', choices=log_levels, default='INFO' )
  parser.add_argument( '--service', action='store_true',
    help='Run headless backend service' )
  args = parser.parse_args()

  options.simulated = args.simulated
  logging.root.setLevel( log_levels[ args.log_level ] )

  if   args.dataviewer:
    import arbwave.gui.dataviewer
    arbwave.gui.dataviewer.main()
    return
  elif args.service:
    try:
      backend.connection.serve()
    except KeyboardInterrupt:
      print 'exiting'
    return
  else:
    # create connection to local drivers by default
    backend.reconnect( dict( __default__ = 'local', local='localhost' ) )
    # we have to do this import _after_ the options. module is modified
    import gui_main
    gui_main.main(args)
    return
