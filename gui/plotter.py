# vim: ts=2:sw=2:tw=80:nowrap


import matplotlib
from matplotlib.figure import Figure

from matplotlib.backends.backend_gtkagg import \
  FigureCanvasGTKAgg as FigCanvas, \
  NavigationToolbar2GTKAgg as NavigationToolbar

from matplotlib.transforms import Bbox, TransformedBbox, \
     blended_transform_factory

from mpl_toolkits.axes_grid1.inset_locator import BboxPatch, BboxConnector,\
     BboxConnectorPatch

from mpl_toolkits.axes_grid import Divider, Size

import numpy as np
import pylab


def connect_bbox( bbox1, bbox2,
                  loc1a, loc2a, loc1b, loc2b,
                  prop_lines, prop_patches=None, prop_patches2_update=None):
  if prop_patches is None:
    prop_patches = prop_lines.copy()
    prop_patches["alpha"] = prop_patches.get("alpha", 1)*0.2
  
  prop_patches2 = prop_patches.copy()
  if prop_patches2_update:
    prop_patches2.update( prop_patches2_update )
  
  c1 = BboxConnector(bbox1, bbox2, loc1=loc1a, loc2=loc2a, **prop_lines)
  c1.set_clip_on(False)
  c2 = BboxConnector(bbox1, bbox2, loc1=loc1b, loc2=loc2b, **prop_lines)
  c2.set_clip_on(False)
  
  bbox_patch1 = BboxPatch(bbox1, **prop_patches2)
  bbox_patch2 = BboxPatch(bbox2, **prop_patches)
  
  p = BboxConnectorPatch(bbox1, bbox2,
                         #loc1a=3, loc2a=2, loc1b=4, loc2b=1,
                         loc1a=loc1a, loc2a=loc2a, loc1b=loc1b, loc2b=loc2b,
                         **prop_patches)
  p.set_clip_on(False)
  
  return c1, c2, bbox_patch1, bbox_patch2, p


def zoom_effect(ax1, ax2, **kwargs):
  u"""
  ax1 : the main axes
  ax1 : the zoomed axes

  Similar to zoom_effect01.  The xmin & xmax will be taken from the
  ax1.viewLim.
  """

  tt = ax1.transScale + (ax1.transLimits + ax2.transAxes)
  trans = blended_transform_factory(ax2.transData, tt)

  mybbox1 = ax1.bbox
  mybbox2 = TransformedBbox(ax1.viewLim, trans)

  prop_patches=kwargs.copy()
  prop_patches["ec"]="none"
  prop_patches["alpha"]=0.2

  c1, c2, bbox_patch1, bbox_patch2, p = \
    connect_bbox(mybbox1, mybbox2,
                 loc1a=3, loc2a=2, loc1b=4, loc2b=1,
                 prop_lines=kwargs, prop_patches=prop_patches,
                 prop_patches2_update={'alpha':0.0})

  ax1.add_patch(bbox_patch1)
  ax2.add_patch(bbox_patch2)
  ax2.add_patch(c1)
  ax2.add_patch(c2)
  ax2.add_patch(p)

  return c1, c2, bbox_patch1, bbox_patch2, p

class ScrollMaster:
  def __init__(self, axes, axes_basis ):
    self.axes = axes
    self.axes_basis = axes_basis

  def onpress(self,event):
    print 'hi'

  def onscroll(self,event):
    event.canvas.grab_focus()
    if event.key is None:
      x0 = self.axes.get_xlim()
      xb = self.axes_basis.get_xlim()

      step = event.step * (x0[1] - x0[0])/10.0

      if ( event.button is 'up'   and not x0[1] >= xb[1] ) or \
         ( event.button is 'down' and not x0[0] <= xb[0] ):
        x1 = ( x0[0]+step, x0[1]+step )
        self.axes.set_xlim(x1)
        event.canvas.draw()

    elif event.key is 'control':
      x0 = self.axes.get_xlim()
      xb = self.axes_basis.get_xlim()

      if (event.button is 'down'   and (x0[0] > xb[0] or x0[1] < xb[1]) ) or \
          event.button is 'up':
        xc = 0.5*( x0[0] + x0[1] )
        xr = ( x0[1] - x0[0] ) * 1.2**(-1*event.step)

        if event.button is 'down' and (xc + xr/2.0) > xb[1] :
          xc = xb[1] - xr/2.0

        if ( xc - xr/2.0 ) < xb[0]:
          x1 = xb
        else:
          x1 = ( xc-xr/2.0, xc+xr/2.0 )
        self.axes.set_xlim(x1)
        event.canvas.draw()



def init_plot():
  dpi = 100
  #  class matplotlib.figure.Figure(figsize=None,
  #                                 dpi=None, facecolor=None,
  #                                 edgecolor=None, linewidth=1.0,
  #                                 frameon=True, subplotpars=None)
  fig = Figure(figsize=(3.0, 3.0), dpi=dpi)
  canvas = FigCanvas(fig)

  rect = [.1, .1, .8, .7 ]
  horiz = [ Size.Scaled(1.0) ]
  vert  = [ Size.Scaled(0.1), Size.Scaled(.20), Size.Scaled(1.), Size.Fixed(.1), Size.Scaled(1.0) ]
  divider = Divider(fig, rect, horiz, vert, aspect=False )
  axes = dict()
  # ##### ANALOG AXES #####
  # The args to add_subplot seem to be
  #    # of rows
  #    # of columns
  #    # pos of this plot in row order
  axes['analog'] = fig.add_axes(rect, label='analog', navigate=True)
  axes['analog'].set_axes_locator( divider.new_locator(nx=0, ny=4) )
  #axes['analog'].set_axis_bgcolor('black')
  axes['analog'].set_ylabel('Output (V)')
  #axes['analog'].xaxis.set_label_position('top')
  axes['analog'].xaxis.set_ticks_position('top')
  pylab.setp(axes['analog'].get_xticklabels(), fontsize=8)
  pylab.setp(axes['analog'].get_yticklabels(), fontsize=8)

  # ##### DIGITAL AXES #####
  axes['digital'] = fig.add_axes(rect, label='digital', navigate=True, sharex=axes['analog'] )
  axes['digital'].set_axes_locator( divider.new_locator(nx=0, ny=2) )
  #axes['digital'].xaxis.set_ticks_position('top')
  pylab.setp(axes['digital'].get_xticklabels(), fontsize=8)
  pylab.setp(axes['digital'].get_yticklabels(), fontsize=8)

  # ##### SCROLL INDICATOR AXES #####
  axes['t'] = fig.add_axes( rect, label='time' )
  axes['t'].set_axes_locator( divider.new_locator(nx=0, ny=0) )
  axes['t'].set_yticks(())
  axes['t'].set_xlabel('Time (s)')

  axes['__scroll_master'] = ScrollMaster( axes['analog'], axes['t'] )
  canvas.mpl_connect('scroll_event', axes['__scroll_master'].onscroll)
  #canvas.connect('key-press-event', axes['__scroll_master'].onpress)
  zoom_effect( axes['digital'], axes['t'] )

  axes['analog'].plot( np.arange(0.,3.,.01), np.sin(2*np.pi* np.arange(0.,3.,.01) ) )
  axes['t'].set_xlim(0.,3.)
  axes['analog'].set_xlim(1.,2.)

  # plot the data as a line series, and save the reference
  # to the plotted line series
  #
  #self.vector = [0]
  #self.plot_data = axes.plot(
  #    self.vector,
  #    linewidth=4,
  #    color=(1, 1, 0),
  #    marker='o',
  #    label="set1",
  #    )[0]

  #self.vector2 = [0]
  #self.plot_data2 = axes.plot(
  #    self.vector2,
  #    linewidth=2,
  #    dashes=[.2,.4],
  #    color=(0, 0, 1),
  #    label="set2",
  #    )[0]

  # leg = axes.legend()
  # # the matplotlib.patches.Rectangle instance surrounding the legend
  # frame  = leg.get_frame()
  # frame.set_facecolor('0.80')    # set the frame face color to light gray
  return axes, fig, canvas

def create(win):
  axes, fig, canvas = init_plot()
  toolbar = NavigationToolbar(canvas, win)

  # self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
  # self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
  # self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
  # self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
  return axes, fig, canvas, toolbar
