# vim: ts=2:sw=2:tw=80:nowrap

from ..gui_callbacks import do_gui_operation
from ... import backend

def plot_stuff( plotter, analog, digital, transitions ):
  t_final = 0.0
  if transitions:
    t_final = max(transitions)
  if analog or digital:
    plotter.start()
  if analog:
    plotter.plot_analog( analog, t_final=t_final )
  if digital:
    plotter.plot_digital( digital, t_final=t_final )
  if analog or digital:
    plotter.finish(t_final=t_final)

def to_plotter( plotter, analog, digital, transitions ):
  do_gui_operation( plot_stuff, plotter, analog, digital, transitions )

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
