# vim: ts=2:sw=2:tw=80:nowrap

import logging, re, glob
import comedi as c

from .... import options
from ....tools.path import collect_prefix

def prefix():
  return 'comedi'


def name():
  return 'Comedi Driver'


def is_simulated():
  return options.simulated


glob_comedi_devices = lambda : glob.glob('/dev/comedi*')

# hook the simulated library if needed
if is_simulated():
  import sim # rehook comedi lib so that hardware is simulated.
  sim.inject_sim_lib()
  glob_comedi_devices = lambda : ['/dev/comedi0']


from device import Device

# mapping from board index to device
devices     = dict()
subdevices  = dict()
analogs     = list()
lines       = list()
counters    = list()
signals     = list()
routed_signals = dict()

def init():
  global devices, subdevices, analogs, lines, counters, signals
  for df in glob_comedi_devices():
    if Device.parse_dev( df ) is None:
      continue # don't match subdevices
    try:
      d = Device( prefix(), df )
    except Exception, e:
      print e
      print 'Could not open comedi device: ', df
      continue
    devices[ str(d) ] = d
    subdevices.update( d.subdevices )
    analogs += [ ao for sub in d.ao_subdevices for ao in sub.channels ]
    lines   += [ do for sub in d.do_subdevices for do in sub.channels ]
    lines   += [ do for sub in d.dio_subdevices for do in sub.channels ]
    counters+= [ co for sub in d.counter_subdevices for co in sub.channels ]
    signals += [ so for  so in d.signals ]
  print 'found {} comedi supported boards'.format(len(devices))


def get_devices():
  """
  Actually, to fit into the framework here for arbwave, we return the subdevices
  """
  return subdevices.values()

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
  # in addition, we use collect_prefix to drop the 'vp/DevX' part of the
  # channel paths
  chans = collect_prefix(channels, 0, 2, 2)
  for d in subdevices:
    if d in config or d in chans:
      subdevices[d].set_config( config.get(d,{}), chans.get(d,[]),
                                shortest_paths, timing_channels )


def set_clocks( clocks ):
  clocks = collect_prefix(clocks, 0, 2, 2)
  for d in subdevices:
    if d in clocks:
      subdevices[d].set_clocks( clocks[d] )


def set_signals( signals ):
  signals = collect_prefix( signals, 0, 2, prefix_list=devices )
  for d in devices:
    devices[d].set_signals( signals.get(d,{}) )


def set_static(analog, digital):
  D = collect_prefix(digital, 0, 2, 2)
  A = collect_prefix(analog, 0, 2, 2)

  for dev, data in D.items():
    subdevices[ dev+'/do' ].set_output( data )

  for dev, data in A.items():
    subdevices[ dev+'/ao' ].set_output( data )


def set_waveforms(analog, digital, transitions, t_max, end_clocks, continuous):
  D = collect_prefix( digital, 0, 2, 2 )
  A = collect_prefix( analog, 0, 2, 2 )
  C = collect_prefix( transitions, 0, 2, 2)
  E = collect_prefix( dict.fromkeys( end_clocks ), 0, 2, 2)

  for d in subdevices:
    if d in D or d in C:
      subdevices[d].set_waveforms( D.get(d,{}), C.get(d,{}), t_max, E.get(d,{}),
                                   continuous )
  for dev in A.items():
    subdevices[ dev[0]+'/ao' ].set_waveforms( dev[1], transitions, t_max, continuous )



def close():
  """
  Close each device.  Each device will first close each of its subdevices.
  """
  while devices:
    devname, dev = devices.popitem()
    logging.debug( 'closing comedi device: %s', devname )
    del dev
