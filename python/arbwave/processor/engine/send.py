# vim: ts=2:sw=2:tw=80:nowrap

import threading, logging
import physical
from ... import backend
from ...tools.gui_callbacks import do_gui_operation
from ...tools.path import collect_prefix
from ...tools.scaling import calculate as calculate_scaling
from ...tools import signal_graphs
from ...tools import signals
from ...gui.storage.var_tools import writevars




def _get_range( scaling, units, offset, globals, **kwargs ):
  """
  Get the minimum and maximum values of a given channels scaling.  Some devices
  can use this to provide more firm limits on channel outputs.  NIDAQmx does
  this, for example.
  """
  if not scaling:
    return kwargs
  # note:  we ignore lines with either empty x _OR_ y values
  mn, mx = calculate_scaling(scaling, units, offset, globals, return_range=True)
  return dict(min=mn, max=mx, **kwargs)




def plot_stuff( plotter, analog, digital, names, t_max ):
  if analog or digital:
    plotter.start( names, t_max )
  if analog:
    plotter.plot_analog( analog )
  if digital:
    plotter.plot_digital( digital )
  if analog or digital:
    plotter.finish()

def to_plotter( plotter, analog, digital, clocks, channels, t_max ):
  names = signals.create_channel_name_map( channels, clocks )
  # take components of device-categorized dictionaries to
  a = signals.merge_signals_sets( [analog] )
  d = signals.merge_signals_sets( [digital] )
  do_gui_operation( plot_stuff, plotter, a, d, names, t_max )

def to_ui_notify( ui, message ):
  do_gui_operation( ui.notify.show, message )

def to_file( analog, digital, transitions, clocks, channels, filename,
             fmt='gnuplot' ):
  fmt = fmt.lower()
  if fmt == 'gnuplot':
    S = signals.merge_signals_sets( [analog, digital] )
    S.to_arrays( transitions, clocks, channels ).save( filename )

  elif fmt == 'python':
    if type(filename) is not str and hasattr(filename, 'write'):
      f = filename
    else:
      f = open(filename, 'w')

    pstyle, pstyle_kwargs = physical.Quantity.get_default_print_style()
    physical.Quantity.set_default_print_style('math')
    writevars(f, dict(
      analog=analog,
      digital=digital,
      transitions=transitions,
      clocks=clocks,
      channels=channels
    ))
    physical.Quantity.set_default_print_style(pstyle, **pstyle_kwargs)

    if f != filename:
      f.close()

  else:
    raise RuntimeError('unknown output file format to save waveform: ' + fmt)

class ToDriver:
  def __init__(self):
    self.sorted_device_list = list()

  def static(self, analog, digital):
    """Send a bunch of static values to each of the drivers"""
    logging.info( 'trying to update the hardware to static output!!!!' )
    for D,driver in backend.all_drivers.items():
      driver.set_static(analog.get(D,{}), digital.get(D,{}))
    logging.debug('updated hardware to static output')


  def waveform(self, analog, digital, transitions, t_max, continuous):
    logging.info( 'trying to update the hardware to waveform output!!!!' )
    if continuous:
      logging.info( 'requesting continuous regeneration...' )

    for D,driver in backend.all_drivers.items():
      driver.set_waveforms(analog.get(D,{}), digital.get(D,{}),
                           transitions, t_max, continuous)
    logging.debug('send waveform to hardware')


  def start(self, devcfg, clocks, signals):
    """
    Send 'go' to each device driver.

    Device inter-dependencies are used to start devices in order of
    most-dependent to least-dependent.
    """
    logging.info( 'sending go signal to all hardware for waveform output' )
    # 1.  Create a graph of signals and clocks; map 'name' to dev
    graph = signal_graphs.build_graph(signals, *clocks)
    to_dev = backend.get_devices() # get_devices returns a new dict everytime
    to_dev.update({ clk[0]:clk[1].device
                    for clk in backend.get_timing_channels().items() })


    # 2.  Add each use device into the graph:
    #   a.  get clock ranges from device.get_config_template
    #   b.  determine the shortest connection to the device--we assume that this
    #       is the connection made by the device to the clock
    #   c.  add the device as a graph node
    #   d.  add a graph edge from this nearest connection to the device
    for dev, cfg in devcfg.items():
      term = signal_graphs.nearest_terminal(
        cfg['clock']['value'],
        set(to_dev[dev].get_config_template()['clock']['range']),
        graph,
      )
      graph.add_node( dev )
      graph.add_edge(term, dev)


    # 3.  Create a list of all devices, sorted by dependency
    #   a.  use a topological sort on the graph
    #   b.  loop through the sorted nodes to generate sorted list of devices
    sorted_nodes = graph.topological_sorted_nodes()
    self.sorted_device_list = list()
    for i in sorted_nodes:
      # only add nodes that correspond to devices and do not add devices
      # more than one time to the list

      if i in to_dev:
        d = to_dev[i]
        if d not in self.sorted_device_list:
          self.sorted_device_list.append( d )
      else:
        # we ignore all intermediate routing nodes, since they are not
        # 'startable'
        pass

    # now we need to reverse the order of the devices since we need clock
    # devices to be last in line
    self.sorted_device_list.reverse()

    for d in self.sorted_device_list:
      d.start()
    logging.info( 'sent go signal all hardware for waveform output' )


  def wait(self):
    """
    Wait for each device driver to finish its single waveform.

    Device inter-dependencies are used to stop devices in order of
    least-dependent to most-dependent (opposite of how they are started).
    """
    def waiter(d):
      d.wait()
    class Waiter( threading.Thread ):
      def __init__(self, target, args=(), kwargs={}):
        super(Waiter,self).__init__()
        self.excObj = None
        self.target,self.args,self.kwargs = target, args, kwargs
      def run(self):
        try:
          logging.debug('Starting wait on %s', self.target)
          self.target(*self.args, **self.kwargs)
        except Exception as e:
          self.excObj = e
          raise
    tids = [ Waiter(target=d.wait) for d in self.sorted_device_list ]
    for t in tids: t.start()
    for t in tids: t.join()
    # return all errors
    return [ t.excObj for t in tids if t.excObj is not None ]


  def stop(self):
    """
    Send 'halt' to each device driver.

    Device inter-dependencies are used to stop devices in order of
    least-dependent to most-dependent (opposite of how they are started).
    """
    logging.info( 'sending stop signal to all hardware for waveform output' )
    for i in range(len(self.sorted_device_list)-1,-1,-1):
      self.sorted_device_list[i].stop()
    logging.info( 'sent stop signal to all hardware for waveform output' )


  def config(self, config, channels, signals, clocks, globals):
    """
    Send device level configuration information to drivers.

    Note that signals and clocks information are needed in order to know how
    various terminals/cables are connected, but this information is sent
    separately via the send.to_driver.clocks(...) and
    send.to_driver.signals(...) functions.
    """
    # we need to calculate the shortest connected paths of all signals
    # these paths are used to determine which terminal a device should
    # connect to in order to use a particular clock.
    # Sending config to drivers also depends on clock changes because
    # drivers may need to know (approximate) rates for clocks.  We don't
    # send in clocks since the clocks have already been configured.
    # We'll rely on engine.send.to_driver.config to send in a link to the
    # timing channels.
    graph = signal_graphs.build_graph(signals, *clocks)

    for vertex in graph.nodes():
      if len(graph.predecessors(vertex)) > 1:
        raise RuntimeError(
          'Double driving terminal/cable ([{}]-->{}) is not allowed!'
          .format(', '.join([v for v in graph.predecessors_iter(vertex)]),
                  vertex)
        )

    C = collect_prefix(config)
    CH= collect_prefix(
      {c['device'] : _get_range( c['scaling'], c['units'], c['offset'],
                                 globals, order=c['order'] )
        for  c in channels.values()
          if c['enable']
      },
      1,
    )

    for D,driver in backend.all_drivers.items():
      driver.set_device_config( C.get(D,{}), CH.get(D,{}), graph )


  def hosts(self, hosts):
    """
      Send host connection configuration information to drivers
      @return whether real connections have been closed/established
    """
    return backend.reconnect( hosts )


  def clocks(self, config):
    """Send clock(s) configuration information to drivers"""
    C = collect_prefix( config )
    for D,driver in backend.all_drivers.items():
      driver.set_clocks( C.get(D,{}) )


  def signals(self, config):
    """Send clock(s) configuration information to drivers"""
    C = collect_prefix( config )
    for D,driver in backend.all_drivers.items():
      driver.set_signals( C.get(D,{}) )


to_driver = ToDriver()
