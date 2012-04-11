# vim: ts=2:sw=2:tw=80:nowrap
import gui
from plotter_toolbar import NavigationToolbar
import digital, analog


class Plotter:
  def __init__(self,win):
    self.axes, self.fig, self.canvas = gui.init_plot()
    self.toolbar = NavigationToolbar(
      self.canvas, win,
      self.axes['hspan-controls'].values(),
      self.axes['vspan-controls'].values(),
    )
    self.axes['__scroll_master'].toolbar = self.toolbar
    self.max_analog = 0.0
    self.max_digital = 0.0
    self.vline = { 't':None, 'digital':None, 'analog':None }

    # self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
    # self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
    # self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
    # self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)

    #import numpy as np
    #self.axes['analog'].plot( np.arange(0.,3.,.01), np.sin(2*np.pi* np.arange(0.,3.,.01) ) )
    #self.axes['t'].set_xlim(0.,3.)
    #self.axes['analog'].set_xlim(1.,2.)

    #self.start()
    #self.plot_digital( digital.example_signals )
    #self.plot_analog( analog.example_signals )
    #self.finish()

  def start(self):
    self.max_analog = 0.0
    self.max_digital = 0.0

  def finish(self, t_final=0.0):
    self.update_t_axes(max_x=t_final)
    self.canvas.draw()

  def plot_analog(self, signals, **kwargs ):
    self.max_analog = analog.plot( self.axes['analog'], signals, **kwargs )

  def plot_digital(self, signals, **kwargs ):
    self.max_digital = digital.plot( self.axes['digital'], signals, **kwargs )

  def update_t_axes(self, max_x=0.0):
    max_x = max( self.max_analog, self.max_digital, max_x )
    xlim = self.axes['analog'].get_xlim()
    self.axes['t'].set_xlim( xlim )
    for a in ['t', 'digital', 'analog']:
      if self.vline[a]:
        try: self.vline[a].remove()
        except: pass
      self.vline[a] = self.axes[a].axvline(
        x=max_x,
        ymin=-1e300,ymax=1e300,
        c="blue",
        linewidth=1,
        zorder=0 )
