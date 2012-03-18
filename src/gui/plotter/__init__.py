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
    self.max_x = 0.0

    # self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
    # self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
    # self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
    # self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)

    #import numpy as np
    #self.axes['analog'].plot( np.arange(0.,3.,.01), np.sin(2*np.pi* np.arange(0.,3.,.01) ) )
    #self.axes['t'].set_xlim(0.,3.)
    #self.axes['analog'].set_xlim(1.,2.)

    self.plot_digital( digital.example_signals )
    self.plot_analog( analog.example_signals )

  def plot_analog(self, signals, **kwargs ):
    """
      kwargs:
        'end_padding' : how much to pad the end of the signal with in order to
                        satisfy the demand that end-transitions be honored
    """
    max_x = analog.plot( self.axes['analog'], signals, **kwargs )
    self.update_t_axes(max_x)

  def plot_digital(self, signals, **kwargs ):
    """
      kwargs:
        'end_padding' : how much to pad the end of the signal with in order to
                        satisfy the demand that end-transitions be honored
    """
    max_x = digital.plot( self.axes['digital'], signals, **kwargs )
    self.update_t_axes(max_x)

  def update_t_axes(self, max_x):
    self.max_x = max( self.max_x, max_x )
    xlim = self.axes['analog'].get_xlim()
    self.axes['t'].set_xlim( xlim )
    for a in ['t', 'digital', 'analog']:
      self.axes[a].axvline(
        x=self.max_x,
        ymin=-1e300,ymax=1e300,
        c="blue",
        linewidth=1,
        zorder=0 )
