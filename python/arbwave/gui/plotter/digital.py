# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting digital signals
"""
from matplotlib.colors import ColorConverter

import numpy as np
from .common import *

# broken_barh( xranges, yrange, **kwargs )
#  xranges : sequence of (xmin, xwidth)
#  yrange  : sequence of (ymin, ywidth)

fc=get_face_color
ls=get_linestyle


def mkbbars(encoding, L, dt, xscale):
  # only pick out the true value transitions
  return [ (L[i][0]*xscale, dt[i]*xscale)   for i in range(len(L)) if L[i][1] ]


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

  channels = list(signals.items())
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
  for chname, grp_data in channels:
    labels.append( get_label( chname ) )
    xscale = get_scale( chname )
    # sort groups by time in last (time,value) element
    groups = sorted(grp_data.items(),
                    key = lambda grp_encdata : grp_encdata[1][1][-1][0])
    dt = mkdt( groups, t_final / xscale )

    for grp, (encoding, data) in groups:
      group_lines[(grp,chname)] = \
        BBWrapper(
          ax.broken_barh(
            mkbbars(encoding, data, dt[grp], xscale), (i,1),
            facecolors=cconv.to_rgba(fc(i)), linewidth=2 ) )
    i += 1

  ax.set_xlabel('Time (s)')
  ax.set_yticks( np.r_[0.5:i] )
  ax.set_yticklabels(labels)
  ax.grid(True)
  return (t_final, ax.get_ylim()), group_lines


# This should be conformant to the output that the arbwave.processor produces.
#
# in the following signals, it is expected that the last transition will be
# honored and that generally the voltage will remain at the given level after
# the signal is finished
#
# format:
#  'channel-label' : {
#    group-number : (encoding, [(start-time, value), ...]),
#    ...
#  }
#
# In the above description, encoding is a description of how the values in the
# group should be interpreted.  Digital values currently ignore encoding.
#
# The start-time is normally in integer number of clock cycles
example_signals = {
  'CH0' : {
    0 : (None, [(0,True), (1000,False), (1100,True), (1200,False)]),
    2 : (None, [(1300,True), (2000,False)]),
    3 : (None, [(2200,True)]),
  },
  'CH1' : {
    0 : (None, [(0,True), (500,False), (800,True), (1000,False)]),
    2 : (None, [(2000,True), (2100,False)]),
    3 : (None, [(2150,True), (2200,False)]),
  },
  'CH2' : {
    0 : (None, [(0,True), (500,False), (800,True), (1000,False)]),
    2 : (None, [(2000,True), (2100,False)]),
  },
  'CH3' : {
    0 : (None, [(100,True), (400,False), (900,True), (1000,False)]),
    2 : (None, [(2000,True), (2100,False)]),
  },
  'CH4' : {
    0 : (None, [(200,True), (600,False), (900,True), (1100,False)]),
    2 : (None, [(2000,True), (2100,False)]),
  },
  'CH5' : {
    0 : (None, [(0,True), (500,False), (800,True), (1000,False)]),
    2 : (None, [(2000,True), (2100,False)]),
  },
  'CH6' : {
    0 : (None, [(0,True), (1000,False), (1100,True), (1200,False)]),
    2 : (None, [(1300,True), (2000,False)]),
  },
  'CH7' : {
    0 : (None, [(0,True), (1000,False), (1100,True), (1200,False)]),
    2 : (None, [(1300,True), (2000,False)]),
  },
  'CH8' : {
    0 : (None, [(0,True), (1000,False), (1100,True), (1200,False)]),
    2 : (None, [(1300,True), (2000,False)]),
  },
}


def plot_test():
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot( ax, example_signals )
  plt.show()
