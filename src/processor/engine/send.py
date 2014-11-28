# vim: ts=2:sw=2:tw=80:nowrap

import threading, logging
from pygraph.algorithms.sorting import topological_sorting
from ...tools.gui_callbacks import do_gui_operation
from ... import backend
from ...tools import signal_graphs
from ...tools import signals

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

def to_file( analog, digital, transitions, clocks, channels, filename=None, fmt=None ):
  S = signals.merge_signals_sets( [analog, digital] )
  S.to_arrays( transitions, clocks, channels ).save( filename, fmt=fmt )

class ToDriver:
  def __init__(self):
    self.sorted_device_list = list()

  def static(self, analog, digital):
    """Send a bunch of static values to each of the drivers"""
    print 'trying to update the hardware to static output!!!!'
    for D in backend.drivers:
      backend.drivers[D].set_static(analog.get(D,{}), digital.get(D,{}))
    logging.debug('updated hardware to static output')


  def waveform(self, analog, digital, transitions, t_max, end_clocks, continuous):
    print 'trying to update the hardware to waveform output!!!!'
    if continuous:
      print 'requesting continuous regeneration...'

    for D in backend.drivers:
      backend.drivers[D].set_waveforms(analog.get(D,{}), digital.get(D,{}),
                                       transitions, t_max, end_clocks,
                                       continuous)
    logging.debug('send waveform to hardware')


  def start(self, devcfg, clocks, signals):
    """
    Send 'go' to each device driver.

    Device inter-dependencies are used to start devices in order of
    most-dependent to least-dependent.
    """
    logging.info( 'sending go signal to all hardware for waveform output' )
    # 1.  Create a graph of signals and clocks; map 'name' to dev
    graph = signal_graphs.build_graph( signals, *clocks )
    to_dev = { d[0]:d[1]  for d in backend.get_devices().items() }

    to_dev.update({ clk[0]:clk[1].device
                      for clk in backend.get_timing_channels().items() })


    # 2.  Add each use device into the graph:
    #   a.  add the device as a graph node
    #   b.  get clock ranges from device.get_config_template
    #   c.  determine the shortest connection to the device--we assume that this
    #       is the connection made by the device to the clock
    #   d.  add a graph edge from this nearest connection to the device
    shortest_paths = signal_graphs.shortest_paths_wgraph(graph, *clocks)
    for dev in devcfg.items():
      graph.add_node( dev[0] )
      term = signal_graphs.nearest_terminal(
        dev[1]['clock']['value'],
        set(to_dev[dev[0]].get_config_template()['clock']['range']),
        shortest_paths )
      graph.add_edge( (term, dev[0]) )


    # 3.  Create a list of all devices, sorted by dependency
    #   a.  use a topological sort on the graph
    #     (pygraph.algorithms.sorting.topological_sort)
    #   b.  loop through the sorted nodes to generate sorted list of devices
    sorted_nodes = topological_sorting(graph)
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
    tids = [ threading.Thread(target=lambda d:d.wait(), args=(d,))
      for d in self.sorted_device_list ]
    for t in tids: t.start()
    for t in tids: t.join()


  def stop(self):
    """
    Send 'halt' to each device driver.

    Device inter-dependencies are used to stop devices in order of
    least-dependent to most-dependent (opposite of how they are started).
    """
    logging.info( 'sending stop signal to all hardware for waveform output' )
    for i in xrange(len(self.sorted_device_list)-1,-1,-1):
      self.sorted_device_list[i].stop()
    logging.info( 'sent stop signal to all hardware for waveform output' )


  def config(self, config, channels, shortest_paths):
    """Send device level configuration information to drivers"""
    timing_channels = backend.get_timing_channels()
    for D in backend.drivers:
      backend.drivers[D].set_device_config( config.get(D,{}),
                                            channels.get(D,{}),
                                            shortest_paths,
                                            timing_channels )


  def clocks(self, config):
    """Send clock(s) configuration information to drivers"""
    for D in backend.drivers:
      backend.drivers[D].set_clocks( config.get(D,{}) )


  def signals(self, config):
    """Send clock(s) configuration information to drivers"""
    for D in backend.drivers:
      backend.drivers[D].set_signals( config.get(D,{}) )


to_driver = ToDriver()
