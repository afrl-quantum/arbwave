# vim: ts=2:sw=2:tw=80:nowrap

import logging
import re
from ...driver import Driver as Base
from ....tools.path import collect_prefix
from ....tools.expand import expand_braces

import nidaqmx
import routes
import task
import channels

class Driver(Base):
  prefix      = 'ni'
  description = 'NIDAQmx Driver'
  has_simulated_mode = True

  def __init__(self, *a, **kw):
    super(Driver,self).__init__(*a, **kw)
    # hook the simulated library if needed
    if self.simulated:
      import sim
      self._old_libnidaqmx = nidaqmx.libnidaqmx.libnidaqmx
      nidaqmx.libnidaqmx.libnidaqmx = sim.NiDAQmx()
      sim.load_nidaqmx_h( nidaqmx )

    # mapping from task name to device
    self.tasks          = dict()
    self.analogs        = list()
    self.lines          = list()
    self.counters       = list()
    self.signals        = list()
    self.routed_signals = dict()

    if not self.nidaqmx_loaded:
      print 'found 0 NI DAQmx boards'
      return

    system = nidaqmx.System()
    print 'found {i} NI DAQmx boards'.format(i=len(system.devices))
    self.rl = routes.RouteLoader(self.host_prefix, self.prefix)
    for d in system.devices:
      product = d.get_product_type()
      logging.debug( 'setting up NIDAQmx routes for device: %s', d )
      self.rl(d, product)

      t = task.Analog(self, '{}/{}'.format(self.prefix,d))
      available = [ channels.Analog('{}/{}'.format(self.prefix,ao), t)
                    for ao in d.get_analog_output_channels()
                      if d.get_analog_output_sample_clock_supported()
                  ]
      if available:
        self.tasks[ str(t) ] = t
        self.analogs += available


      t = task.Digital(self, '{}/{}'.format(self.prefix,d))
      available = [ channels.Digital('{}/{}'.format(self.prefix,do), t)
                    for do in d.get_digital_output_lines()
                      if nidaqmx.physical.get_do_sample_clock_supported(do)
                  ]
      if available:
        self.tasks[ str(t) ] = t
        self.lines += available


      t = task.Timing(self, '{}/{}'.format(self.prefix,d))
      available = [ channels.Timing('{}/{}'.format(self.prefix,co), t)
                    for co in d.get_counter_output_channels() ]
      if available:
        self.tasks[ str(t) ] = t
        self.counters += available

    for src, dest in self.rl.aggregate_map.items():
      logging.log(logging.DEBUG-1,
        'creating NIDAQmx backplane channel: %s --> %s', src, dest
      )
      self.signals.append(
        channels.Backplane(src,destinations=dest,invertible=True)
      )

  @property
  def nidaqmx_loaded(self):
    return False if nidaqmx.libnidaqmx.libnidaqmx is None else True


  def close(self):
    """
    Set all channels to a save value, close all devices, and uninitialize stuff
    """
    # delete all nidaqmx tasks
    devices = set()
    while self.tasks:
      devname, dev = self.tasks.popitem()
      logging.debug( 'closing NIDAQmx device: %s', devname )
      if dev.task:
        devices.update( dev.task.get_devices() )
      dev.clear()
      del dev

    # now unroute all signals
    system = nidaqmx.System()
    for route in self.routed_signals.keys():
      if 'External/' in route[0] or 'External/' in route[1]:
        continue

      s, d = self.rl.signal_route_map[ route ]
      system.disconnect_terminals( s, d )
      system.tristate_terminal(d) # an attempt to protect the dest terminal

    # finish off by reseting the devices that were used
    if not self.nidaqmx_loaded: return
    for d in system.devices:
      if str(d) in devices:
        d.reset()

    if self.simulated:
      # restore the nidaqmx lib
      nidaqmx.libnidaqmx.libnidaqmx = self._old_libnidaqmx

  def get_devices(self):
    """
    Returns the set of configurable tasks..
    """
    return self.tasks.values()

  def get_analog_channels(self):
    return self.analogs

  def get_digital_channels(self):
    return self.lines

  def get_timing_channels(self):
    return self.counters

  def get_routeable_backplane_signals(self):
    return self.signals


  def set_device_config( self, config, channels, shortest_paths ):
    # we need to separate channels first by device
    # (configs are already naturally separated by device)
    chans = { k:dict()  for k in self.tasks }
    for c in channels:
      m = re.match( '((' + self.prefix + '/Dev[0-9]*/[ap]o).*)', c)
      # we change '/po' to '/do' to correspond with the task name given above for
      # digital channels.
      chans[ m.group(2).replace('/po','/do') ][ m.group(1) ] = channels[c]
    chans = { k:v  for k,v in chans.items()  if v }

    for d,T in self.tasks.items():
      if d in config or d in chans:
        T.set_config( config.get(d,{}), chans.get(d,{}), shortest_paths )


  def set_clocks( self, clocks ):
    clocks = collect_prefix(clocks, 0, 2)
    for d,T in self.tasks.items():
      if d in clocks:
        T.set_clocks( clocks[d] )


  def set_signals( self, signals ):
    """
    NIDAQmx signal router.

    This router does not happen in the task, since we use System.connect_terminals
    instead of task.export_signal.
    """
    if self.routed_signals != signals:
      system = nidaqmx.System()
      old = set( self.routed_signals.keys() )
      new = set( signals.keys() )

      # disconnect routes no longer in use
      for route in ( old - new ):
        if 'External/' in route[0] or 'External/' in route[1]:
          continue

        s, d = self.rl.signal_route_map[ route ]
        system.disconnect_terminals( s, d )
        system.tristate_terminal(d) # an attempt to protect the dest terminal

      # connect new routes routes no longer in use
      for route in ( new - old ):
        if 'External/' in route[0] or 'External/' in route[1]:
          continue

        s, d = self.rl.signal_route_map[ route ]
        if s is None or d is None:
          continue # None means an external connection
        system.connect_terminals(s, d, signals[route]['invert'])

      self.routed_signals = signals


  def set_static(self, analog, digital):
    D = collect_prefix(digital, 0, 2)
    A = collect_prefix(analog, 0, 2)

    for dev, data in D.items():
      self.tasks[ dev+'/do' ].set_output( data )

    for dev, data in A.items():
      self.tasks[ dev+'/ao' ].set_output( data )


  def set_waveforms( self, analog, digital, transitions,
                     t_max, end_clocks, continuous ):
    """
    Viewpoint ignores all transition information since it only needs absolute
    timing information.
    """
    D = collect_prefix( digital, 0, 2 )
    A = collect_prefix( analog, 0, 2 )

    for dev in D.items():
      self.tasks[ dev[0]+'/do' ] \
        .set_waveforms( dev[1], transitions, t_max, continuous )

    for dev in A.items():
      self.tasks[ dev[0]+'/ao' ] \
        .set_waveforms( dev[1], transitions, t_max, continuous )
