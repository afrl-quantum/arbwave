# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting digital signals
"""
from matplotlib.colors import ColorConverter

import numpy as np
from common import *

# broken_barh( xranges, yrange, **kwargs )
#  xranges : sequence of (xmin, xwidth)
#  yrange  : sequence of (ymin, ywidth)

fc=get_face_color
ls=get_linestyle


def mkbbars( L, dt, xscale ):
  # only pick out the true value transitions
  return [ (L[i][0]*xscale, dt[i]*xscale)   for i in xrange(len(L)) if L[i][1] ]


class BBWrapper(object):
  def __init__(self, bb):
    self.bb = bb
  def get_color(self, *args, **kwargs):
    return self.bb.get_facecolor(*args, **kwargs)[0]
  def set_color(self, *args, **kwargs):
    self.bb.set_facecolor(*args, **kwargs)
  def get_linewidth(self, *args, **kwargs):
    return self.bb.get_linewidth(*args, **kwargs)
  def set_linewidth(self, *args, **kwargs):
    self.bb.set_linewidth(*args, **kwargs)


def plot( ax, signals, name_map=None, t_final=None ):
  if t_final is None:
    #start by finding the maximum time
    t_final = get_t_final( signals )
    t_final *= 1.001

  channels = signals.items()
  if name_map:
    channels.sort( key = lambda v: -name_map[v[0]]['order'] )
    get_label = lambda n : name_map[n]['name']
    get_scale = lambda n : float(name_map[n]['dt_clk']) #strip units
  else:
    channels.sort( key = lambda v:v[0] ) # reverse lexical sort
    get_label = lambda n : n
    get_scale = lambda n : 1.0 # scaled by unity

  cconv = ColorConverter()

  ax.clear()
  labels = list()
  i = 0
  group_lines = dict()
  for c in channels:
    labels.append( get_label( c[0] ) )
    xscale = get_scale( c[0] )
    dt = mkdt( c[1], t_final / xscale )

    groups = c[1].items()
    groups.sort( key = lambda v : v[0] )
    for g in groups:
      group_lines[(g[0],c[0])] = \
        BBWrapper(
          ax.broken_barh(
            mkbbars( g[1], dt[ g[0] ], xscale ), (i,1),
            facecolors=cconv.to_rgba(fc(i)), linewidth=2 ) )
    i += 1

  ax.set_xlabel('Time (s)')
  ax.set_yticks( np.r_[0.5:i] )
  ax.set_yticklabels(labels)
  ax.grid(True)
  return (t_final, ax.get_ylim()), group_lines


# This should be conformant to the output that the arbwave.Processor produces.
#
# in the following signals, it is expected that the last transition will be
# honored and that generally the voltage will remain at the given level after
# the signal is finished
#
# format:
#  'channel-label' : {
#    group-number : [(start-time, value), ...],
#    ...
#  }
#
# The start-time is normally in integer number of clock cycles
example_signals = {
  'CH0' : {
    0 : [(0,True), (1000,False), (1100,True), (1200,False)],
    2 : [(1300,True), (2000,False)],
    3 : [(2200,True)],
  },
  'CH1' : {
    0 : [(0,True), (500,False), (800,True), (1000,False)],
    2 : [(2000,True), (2100,False)],
    3 : [(2150,True), (2200,False)],
  },
  'CH2' : {
    0 : [(0,True), (500,False), (800,True), (1000,False)],
    2 : [(2000,True), (2100,False)],
  },
  'CH3' : {
    0 : [(100,True), (400,False), (900,True), (1000,False)],
    2 : [(2000,True), (2100,False)],
  },
  'CH4' : {
    0 : [(200,True), (600,False), (900,True), (1100,False)],
    2 : [(2000,True), (2100,False)],
  },
  'CH5' : {
    0 : [(0,True), (500,False), (800,True), (1000,False)],
    2 : [(2000,True), (2100,False)],
  },
  'CH6' : {
    0 : [(0,True), (1000,False), (1100,True), (1200,False)],
    2 : [(1300,True), (2000,False)],
  },
  'CH7' : {
    0 : [(0,True), (1000,False), (1100,True), (1200,False)],
    2 : [(1300,True), (2000,False)],
  },
  'CH8' : {
    0 : [(0,True), (1000,False), (1100,True), (1200,False)],
    2 : [(1300,True), (2000,False)],
  },
}


if __name__ == '__main__':
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot( ax, example_signals )
  plt.show()
