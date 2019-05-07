# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import sys, argparse, logging
import cProfile, pstats

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
    import multiprocessing as mp # is this ok for windows?
    mp.set_start_method('spawn')

  parser = argparse.ArgumentParser(prog='Arbwave')
  parser.add_argument( '--version', action='version',
    version='%(prog)s '+version.version() )
  parser.add_argument( 'filename', nargs='?', help='configuration file' )
  parser.add_argument( '--simulated', action='store_true',
    help='Use simulated hardware' )
  parser.add_argument( '--dataviewer', action='store_true',
    help='Start only the data viewer' )
  parser.add_argument( '--log-level', choices=log_levels, default='INFO' )
  parser.add_argument( '--service', metavar='ADDRESS[:PORT]', action='store',
    const='0.0.0.0', nargs='?', default='',
    help='Run headless backend service after binding to the optional address '
         'and port.  Note that 0.0.0.0 is valid, though the addresses '
         'returned to the remote client will be set to match whatever '
         'address/port the client actually connects to.' )
  parser.add_argument( '--ipython', action='store_true',
    help='Attempt to use ipython as embedded shell' )
  parser.add_argument( '--disable', action='append', default=[],
    choices=backend.connection.get_driver_list(),
    help='Disable specific driver' )
  parser.add_argument('--pyro-ns', metavar='NAMESERVER[:PORT]',
    help='Specify Pyro nameserver address (in case it cannot be reached by UDP '
         'broadcasts).  This option will only affect those backends that use '
         'the Pyro Nameserver.  The default behavior will be to use a '
         'broadcast search to find the Pyro Nameserver (which only works if it '
         'is on the same subnet).')
  parser.add_argument('--profile', nargs='?', metavar='FILENAME', default=0,
    help='Run this script under the observation of a profiler, optionally '
         'writing out to the given file.  There are a few tools that can '
         'convert the gprof output to easier material to visualize.')
  args = parser.parse_args()

  options.simulated = args.simulated
  options.ipython = args.ipython
  options.disabled_drivers = set(args.disable)
  options.pyro_ns = args.pyro_ns
  logging.root.setLevel( log_levels[ args.log_level ] )

  if args.profile != 0:
    options.pstats = pstats.Stats()
    profiler = cProfile.Profile()
    profiler.enable()
  if   args.dataviewer:
    import arbwave.gui.dataviewer
    arbwave.gui.dataviewer.main()
  elif args.service:
    try:
      backend.connection.serve(*args.service.split(':'), ns=options.pyro_ns)
    except KeyboardInterrupt:
      print('exiting')
  else:
    # we have to do this import _after_ the options. module is modified
    from . import gui_main
    gui_main.main(args)

  if args.profile != 0:
    profiler.disable()
    options.pstats.add(profiler) # add main gui thread profiler
    if args.profile is None:
      options.pstats.print_stats()
    else:
      options.pstats.dump_stats(args.profile)
