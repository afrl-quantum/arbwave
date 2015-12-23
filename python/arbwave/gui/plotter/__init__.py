# vim: ts=2:sw=2:tw=80:nowrap
import gui
from plotter_toolbar import NavigationToolbar
import digital, analog
import common

class Highlighter(object):
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


class Plotter(object):
  def __init__(self,win):
    self.axes, self.fig, self.canvas = gui.init_plot()
    self.toolbar = NavigationToolbar(
      self.canvas, win,
      self.axes['hspan-controls'].values(),
      self.axes['vspan-controls'].values(),
      self.set_max_ranges,
    )
    self.axes['__scroll_master'].toolbar = self.toolbar
    self.ranges = dict( analog=(0,(0,0)), digital=(0,(0,0)) )
    self.vline = { 't':None, 'digital':None, 'analog':None }
    self.lines = dict()
    self.highlighted = None
    self.group_lines = dict()
    self.highlighted_parts = list()

    self.xlim = None
    self.xview = None
    self.yview = {'analog':None,'digital':None}


  def set_max_ranges(self):
    self.xlim = (0.0,self.ranges['analog'][0])
    self.axes['t'].set_xlim( self.xlim )
    self.axes['analog' ].set_xlim( self.xlim )
    self.axes['analog' ].set_ylim( self.ranges['analog' ][1] )
    self.axes['digital'].set_ylim( self.ranges['digital'][1] )
    self.canvas.draw()


  def start(self, names=None, t_final=0.0):
    if self.xview is not None:
      self.xview = self.axes['analog'].get_xlim()
      self.yview['analog'] = self.axes['analog'].get_ylim()
      self.yview['digital'] = self.axes['digital'].get_ylim()
    self.ranges = dict( analog=(0,0), digital=(0,0) )
    self.lines = dict()
    self.group_lines = dict()
    self.names = names
    self.t_final = t_final

  def finish(self, t_final=None):
    if t_final is not None: self.t_final=t_final
    self.xlim = self.axes['analog'].get_xlim()
    if self.xview is None:
      self.xview = self.axes['analog'].get_xlim()
      self.yview['analog'] = self.axes['analog'].get_ylim()
      self.yview['digital'] = self.axes['digital'].get_ylim()
    else:
      self.axes['analog'].set_xlim(  self.xview )
      self.axes['analog'].set_ylim(  self.yview['analog'] )
      self.axes['digital'].set_ylim( self.yview['digital'] )
    self.update_t_axes(max_x=self.t_final)
    self.canvas.draw()

  def plot_analog(self, signals, names=None, t_final=None, *args, **kwargs ):
    if names is not None:   self.names = names
    if t_final is not None: self.t_final=t_final
    self.ranges['analog'], lines, group_lines = analog.plot(
      self.axes['analog'], signals, self.names, self.t_final, *args, **kwargs
    )
    for l in lines.items():
      # we add the analog prefix back on for ease later
      self.lines[ l[0] ] = Highlighter( l[1] )
    self.group_lines.update(
      {g[0]:Highlighter(g[1]) for g in group_lines.items()} )

  def plot_digital(self, signals, names=None, t_final=None, *args, **kwargs ):
    if names is not None:   self.names = names
    if t_final is not None: self.t_final=t_final
    self.ranges['digital'], group_lines = digital.plot(
      self.axes['digital'], signals, self.names, self.t_final, *args, **kwargs
    )
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
    max_x = max( self.ranges['analog'][0], self.ranges['digital'][0], max_x )
    self.axes['t'].set_xlim( self.xlim )
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