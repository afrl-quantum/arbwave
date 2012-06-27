# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting digital signals
"""
import pylab
from matplotlib.colors import ColorConverter

import numpy as np
from common import *

# broken_barh( xranges, yrange, **kwargs )
#  xranges : sequence of (xmin, xwidth)
#  yrange  : sequence of (ymin, ywidth)

fc=get_face_color
ls=get_linestyle


def mkbbars( L, dt ):
  # only pick out the true value transitions
  return [ (L[i][0], dt[i])   for i in xrange(len(L))  if L[i][1] ]


class BBWrapper:
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


def plot( ax, signals, names=None, t_final=None ):
  if t_final is None:
    #start by finding the maximum time
    t_final = get_t_final( signals )
    t_final *= 1.001

  channels = signals.items()
  channels.sort( key = lambda v:v[0] ) # reverse lexical sort

  if names:
    get_label = lambda n : names[n]
  else:
    get_label = lambda n : n

  cconv = ColorConverter()

  ax.clear()
  labels = list()
  i = 0
  group_lines = dict()
  for c in channels:
    labels.append( get_label( c[0] ) )
    dt = mkdt( c[1], t_final )

    groups = c[1].items()
    groups.sort( key = lambda v : v[0] )
    for g in groups:
      group_lines[(g[0],c[0])] = \
        BBWrapper(
          ax.broken_barh(
            mkbbars( g[1], dt[ g[0] ] ), (i,1),
            facecolors=cconv.to_rgba(fc(i)), linewidth=2 ) )
    i += 1

  ax.set_xlabel('Time (s)')
  ax.set_yticks( np.r_[0.5:i] )
  ax.set_yticklabels(labels)
  pylab.setp(ax.get_xticklabels(), fontsize=8)
  pylab.setp(ax.get_yticklabels(), fontsize=8)
  ax.grid(True)
  return t_final, group_lines


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
# Which pieces of the 3-tuple (start-time, number-samples, value) is
# needed/ignored really depends on what is using this information.  For
# plotting as well as hardware output with an Viewpoint DIO-64 cards, the
# number-samples component will be ignored.  For digital output on cards like
# National Instruments digital output card 6533(?), start-time will be ignored.
example_signals = {
  'CH0' : {
    0 : [(0,True), (100,False), (110,True), (120,False)],
    2 : [(130,True), (200,False)],
    3 : [(220,True)],
  },
  'CH1' : {
    0 : [(0,True), (50,False), (80,True), (100,False)],
    2 : [(200,True), (210,False)],
    3 : [(215,True), (220,False)],
  },
  'CH2' : {
    0 : [(0,True), (50,False), (80,True), (100,False)],
    2 : [(200,True), (210,False)],
  },
  'CH3' : {
    0 : [(10,True), (40,False), (90,True), (100,False)],
    2 : [(200,True), (210,False)],
  },
  'CH4' : {
    0 : [(20,True), (60,False), (90,True), (110,False)],
    2 : [(200,True), (210,False)],
  },
  'CH5' : {
    0 : [(0,True), (50,False), (80,True), (100,False)],
    2 : [(200,True), (210,False)],
  },
  'CH6' : {
    0 : [(0,True), (100,False), (110,True), (120,False)],
    2 : [(130,True), (200,False)],
  },
  'CH7' : {
    0 : [(0,True), (100,False), (110,True), (120,False)],
    2 : [(130,True), (200,False)],
  },
  'CH8' : {
    0 : [(0,True), (100,False), (110,True), (120,False)],
    2 : [(130,True), (200,False)],
  },
}


if __name__ == '__main__':
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot( ax, example_signals )
  plt.show()
