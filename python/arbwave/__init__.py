# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import sys, argparse, logging
try:
  import hotshot
  import hotshot.stats
  has_hotshot = True
except:
  has_hotshot = False

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
  parser.add_argument( '--service', action='store_true',
    help='Run headless backend service' )
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
  if has_hotshot:
    parser.add_argument('--profile',
      help='Run this script under the observation of a profiler, writing out to '
           'the given file.  In order to show results, one can use the '
           '--profile-show,--profile-sort options.  Perhaps an even '
           'better way to visualize the profliing results is to use '
           'kcachegrind:  first convert the results file from this '
           'profile to calltree format by using: '
           '"hotshot2calltree file.prof > file.calltree"')
    parser.add_argument('--profile-show', metavar='PROFILE',
      help='Calculate the results of a previous profile and show the top PROFILE_N '
           'worst offenders')
    parser.add_argument('--profile-sort', type=str, default=['time', 'calls'],
      help='Specify the columns to sort by [Default: time, calls]. All '
           'possible columns are: ' +
           ', '.join(hotshot.stats.pstats.Stats.sort_arg_dict_default.keys()))
    parser.add_argument('--profile-n', type=int, default=20,
      help='Specify the number of top offenders to show when showing '
           'profile results [Default: 20]')
  args = parser.parse_args()

  if has_hotshot and args.profile_show:
    # sort the output based on time spent in the function
    # print the top 20 culprits
    stats = hotshot.stats.load(args.profile_show)
    stats.sort_stats(args.profile_sort)
    stats.print_stats(args.profile_n)
    return

  options.simulated = args.simulated
  options.ipython = args.ipython
  options.disabled_drivers = set(args.disable)
  options.pyro_ns = args.pyro_ns
  logging.root.setLevel( log_levels[ args.log_level ] )

  if has_hotshot and args.profile:
    profiler = hotshot.Profile(args.profile)
    profiler.start()
  if   args.dataviewer:
    import arbwave.gui.dataviewer
    arbwave.gui.dataviewer.main()
  elif args.service:
    try:
      backend.connection.serve(ns=options.pyro_ns)
    except KeyboardInterrupt:
      print('exiting')
  else:
    # create connection to local drivers by default
    backend.reconnect( dict( __default__ = 'local', local='localhost' ) )
    # we have to do this import _after_ the options. module is modified
    from . import gui_main
    gui_main.main(args)

  if has_hotshot and args.profile:
    profiler.stop()
    profiler.close()
