# vim: ts=2:sw=2:tw=80:nowrap
import gui
from plotter_toolbar import NavigationToolbar
import digital, analog
import common

class Highlighter:
  def __init__(self, line):
    self.line = line
    self.color = line.get_color()
    self.linewidth = line.get_linewidth()
  def highlight(self):
    if common.highlight_color:
      self.line.set_color( common.highlight_color )
    if common.highlight_linewidth:
      self.line.set_linewidth( common.highlight_linewidth )
    if common.highlight_alpha:
      c = list( self.line.get_color() )
      c[3] = common.highlight_alpha
      self.line.set_color( c )
  def unhighlight(self):
    self.line.set_color( self.color )
    self.line.set_linewidth( self.linewidth )


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
    self.lines = dict()
    self.highlighted = None
    self.group_lines = dict()
    self.highlighted_parts = list()

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
    self.group_lines = dict()

  def finish(self, t_final=0.0):
    self.update_t_axes(max_x=t_final)
    self.canvas.draw()

  def plot_analog(self, signals, *args, **kwargs ):
    self.max_analog, lines, group_lines \
      = analog.plot( self.axes['analog'], signals, *args, **kwargs )
    # purge all old analog lines
    self.lines = { l[0]:l[1]  for l in self.lines.items()  if l[0].startswith('Analog/') }
    for l in lines.items():
      # we add the analog prefix back on for ease later
      self.lines['Analog/' + l[0]] = Highlighter( l[1] )
    self.group_lines.update(
      {g[0]:Highlighter(g[1]) for g in group_lines.items()} )

  def plot_digital(self, signals, *args, **kwargs ):
    self.max_digital, group_lines \
      = digital.plot( self.axes['digital'], signals, *args, **kwargs )
    self.group_lines.update(
      {g[0]:Highlighter(g[1]) for g in group_lines.items()} )

  def highlight(self, physical_channel):
    if self.highlighted:
      self.highlighted.unhighlight()
      self.highlighted = None
    if physical_channel in self.lines:
      self.lines[physical_channel].highlight()
      self.highlighted = self.lines[physical_channel]
    self.canvas.draw()

  def highlight_parts(self, pkeys):
    if self.highlighted_parts:
      for hp in self.highlighted_parts: hp.unhighlight()
      self.highlighted_parts = list()
    for p in pkeys:
      if p in self.group_lines:
        gl = self.group_lines[p]
        gl.highlight()
        self.highlighted_parts.append( gl )
    self.canvas.draw()

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
