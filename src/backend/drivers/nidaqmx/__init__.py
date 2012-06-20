# vim: ts=2:sw=2:tw=80:nowrap

import logging
import re
from .... import options
from ....path import collect_prefix
from ....expand import expand_braces

import nidaqmx

def prefix():
  return 'ni'


def name():
  return 'NIDAQmx Driver'


def is_simulated():
  return options.simulated


# hook the simulated library if needed
if is_simulated():
  import sim
  nidaqmx.libnidaqmx.libnidaqmx = sim.NiDAQmx()
  sim.load_nidaqmx_h( nidaqmx )

import task
import routes
import channels

# mapping from task name to device
tasks     = dict()
analogs   = list()
lines     = list()
counters  = list()
signals   = list()
routed_signals = dict()



def format_terminals(d, dest):
  prfx = prefix()
  # for some terminals, we must use a non ni-formatted path to work with
  # the other devices.  An example is 'TRIG/0'.
  # Furthermore, we are required to indicate which terminals can be
  # connected to external cables/busses
  if type(dest) in [ tuple, list ]:
    # we are given both native and recognizable terminal formats
    D  = expand_braces(dest[0])
    if dest[1]:
      ND = expand_braces('{p}/{d}/{T}'.format(p=prfx,d=d,T=dest[1]))
      assert len(D) == len(ND), \
        'NIDAQmx: {d} has mismatch terminals to native terminals: {s}' \
        .format(d=d,s=repr(dest))
    else:
      ND = [None] # must be something like an 'External/' connection
  else:
    # only native terminal formats
    D = expand_braces('{p}/{d}/{T}'.format(p=prfx,d=d,T=dest))
    ND = D
  return D, ND



def load_all():
  global tasks, analogs, lines, counters, signals
  system = nidaqmx.System()
  print 'found {i} NI DAQmx boards'.format(i=len(system.devices))
  prfx = prefix()
  for d in system.devices:
    product = d.get_product_type()
    for sources in routes.available[product]:
      dest = list()
      ni_dest = list()
      for dest_i in routes.available[product][sources]:
        D, ND = format_terminals(d, dest_i)
        dest        += D
        ni_dest += ND
      src, ni_src = format_terminals(d, sources)
      for i in xrange( len(src) ):
        for j in xrange( len(dest) ):
          routes.signal_route_map[ (src[i], dest[j]) ] = (ni_src[i], ni_dest[j])

        signals.append(
          channels.Backplane( src[i],
                              destinations=dest,
                              invertible = True ) )


    if d.get_analog_output_sample_clock_supported():
      t = task.Analog('{}/{}'.format(prfx,d))
      available = [ channels.Analog('{}/{}'.format(prfx,ao), t)
                    for ao in d.get_analog_output_channels()
                  ]
      if available:
        tasks[ str(t) ] = t
        analogs += available


    t = task.Digital('{}/{}'.format(prfx,d))
    available = [ channels.Digital('{}/{}'.format(prfx,do), t)
                  for do in d.get_digital_output_lines()
                    if nidaqmx.physical.get_do_sample_clock_supported(do)
                ]
    if available:
      tasks[ str(t) ] = t
      lines += available


    t = task.Timing('{}/{}'.format(prfx,d))
    available = [ channels.Timing('{}/{}'.format(prfx,co), t)
                  for co in d.get_counter_output_channels() ]
    if available:
      counters += available
      tasks[ str(t) ] = t


load_all()

def get_devices():
  """
  Returns the set of configurable tasks..
  """
  return tasks.values()

def get_analog_channels():
  return analogs

def get_digital_channels():
  return lines

def get_timing_channels():
  return counters

def get_routeable_backplane_signals():
  return signals


def set_device_config( config, channels, shortest_paths, timing_channels ):
  # we need to separate channels first by device
  # (configs are already naturally separated by device)
  chans = { k:dict()  for k in tasks }
  for c in channels:
    m = re.match( '((' + prefix() + '/Dev[0-9]*/[ap]o).*)', c)
    # we change '/po' to '/do' to correspond with the task name given above for
    # digital channels.
    chans[ m.group(2).replace('/po','/do') ][ m.group(1) ] = channels[c]

  for d in tasks:
    if d in config or d in chans:
      tasks[d].set_config( config.get(d,{}), chans.get(d,{}), shortest_paths, timing_channels )


def set_clocks( clocks ):
  clocks = collect_prefix(clocks, 0, 2)
  for d in tasks:
    if d in clocks:
      tasks[d].set_clocks( clocks[d] )


def strip_prefix( s ):
  if s:
    return s.partition('/')[-1]
  return s

def set_signals( signals ):
  """
  NIDAQmx signal router.

  This router does not happen in the task, since we use System.connect_terminals
  instead of task.export_signal.
  """
  global routed_signals
  if routed_signals != signals:
    system = nidaqmx.System()
    old = set( routed_signals.keys() )
    new = set( signals.keys() )

    # disconnect routes no longer in use
    for route in ( old - new ):
      if 'External/' in route[0] or 'External/' in route[1]:
        continue

      s, d = routes.signal_route_map[ route ]
      s, d = strip_prefix(s), strip_prefix(d)
      system.disconnect_terminals( s, d )
      system.tristate_terminal(d) # an attempt to protect the dest terminal

    # connect new routes routes no longer in use
    for route in ( new - old ):
      if 'External/' in route[0] or 'External/' in route[1]:
        continue

      s, d = routes.signal_route_map[ route ]
      s, d = strip_prefix(s), strip_prefix(d)
      if s is None or d is None:
        continue # None means an external connection
      system.connect_terminals(s, d, signals[route]['invert'])

    routed_signals = signals


def set_static(analog, digital):
  D = collect_prefix(digital, 0, 2)
  A = collect_prefix(analog, 0, 2)

  for dev in D.items():
    tasks[ dev[0]+'/do' ].set_output( dev[1] )

  for dev in A.items():
    tasks[ dev[0]+'/ao' ].set_output( dev[1] )


def set_waveforms(analog, digital, transitions, t_max, continuous):
  """
  Viewpoint ignores all transition information since it only needs absolute
  timing information.
  """
  D = collect_prefix( digital, 0, 2 )
  A = collect_prefix( analog, 0, 2 )

  for dev in D.items():
    tasks[ dev[0]+'/do' ].set_waveforms( dev[1], transitions, t_max, continuous )

  for dev in A.items():
    tasks[ dev[0]+'/ao' ].set_waveforms( dev[1], transitions, t_max, continuous )


def start_output():
  # FIXME:  clocks will probably need to be started last.  This means, if a
  # particular viewpoint card has a channel being used as a clock, the card will
  # likely have to be started later
  for dev in tasks.values():
    dev.start_output()


def stop_output():
  for dev in tasks.values():
    dev.stop_output()


def close():
  """
  Set all channels to a save value, close all devices, and uninitialize stuff
  """
  devices = set()
  while tasks:
    devname, dev = tasks.popitem()
    logging.debug( 'closing NIDAQmx device: %s', devname )
    if dev.task:
      devices.update( dev.task.get_devices() )
    dev.clear()
    del dev

  # now unroute all signals
  global routed_signals
  system = nidaqmx.System()
  for route in routed_signals.keys():
    if 'External/' in route[0] or 'External/' in route[1]:
      continue

    s, d = routes.signal_route_map[ route ]
    s, d = strip_prefix(s), strip_prefix(d)
    system.disconnect_terminals( s, d )
    system.tristate_terminal(d) # an attempt to protect the dest terminal

  # finish off by reseting the devices that were used
  for d in system.devices:
    if str(d) in devices:
      d.reset()
