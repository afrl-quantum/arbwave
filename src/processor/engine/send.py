# vim: ts=2:sw=2:tw=80:nowrap

from ..gui_callbacks import do_gui_operation
from ... import backend

def plot_stuff( plotter, analog, digital, names, t_max ):
  if analog or digital:
    plotter.start()
  if analog:
    plotter.plot_analog( analog, names, t_max )
  if digital:
    plotter.plot_digital( digital, names, t_max )
  if analog or digital:
    plotter.finish(t_final=t_max)

def to_plotter( plotter, analog, digital, channels, t_max ):
  # we need a map from device-name to channel name
  names = dict()
  for c in channels.items():
    dev = c[1]['device']
    if dev and c[1]['enable']:
      if dev in names:
        raise NameError('Device channels can only be used once')
      # the partition is to get rid of the 'Analog/' or 'Digital/' prefix
      names[ c[1]['device'].partition('/')[2] ] = c[0]


  # take components of device-categorized dictionaries to
  a = dict()
  for D in analog.values():
    a.update(D)
  d = dict()
  for D in digital.values():
    d.update(D)

  do_gui_operation( plot_stuff, plotter, a, d, names, t_max )

class ToDriver:
  def static(self, analog, digital):
    """Send a bunch of static values to each of the drivers"""
    print 'trying to update the hardware to static output!!!!'
    for D in backend.drivers:
      backend.drivers[D].set_static(analog.get(D,{}), digital.get(D,{}))


  def waveform(self, analog, digital, transitions, t_max, continuous):
    print 'trying to update the hardware to waveform output!!!!'
    if continuous:
      print 'requesting continuous regeneration...'

    for D in backend.drivers:
      backend.drivers[D].set_waveforms(analog.get(D,{}), digital.get(D,{}),
                                       transitions, t_max, continuous)


  def stop(self):
    """Send 'halt' to each device driver. """
    for D in backend.drivers:
      backend.drivers[D].stop_output()


  def config(self, config, channels):
    """Send device level configuration information to drivers"""
    for D in backend.drivers:
      backend.drivers[D].set_device_config(config.get(D,{}), channels.get(D,{}))


  def clocks(self, config):
    """Send clock(s) configuration information to drivers"""
    for D in backend.drivers:
      backend.drivers[D].set_clocks( config.get(D,{}) )


  def signals(self, config):
    """Send clock(s) configuration information to drivers"""
    for D in backend.drivers:
      backend.drivers[D].set_signals( config.get(D,{}) )


to_driver = ToDriver()
