# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting digital signals
"""
import pylab

import numpy as np
from common import *

# broken_barh( xranges, yrange, **kwargs )
#  xranges : sequence of (xmin, xwidth)
#  yrange  : sequence of (ymin, ywidth)

fc=get_face_color
ls=get_linestyle


def mkbbars( L, dt ):
  # only pick out the true value transitions
  return [ (L[i][0], dt[i])   for i in xrange(len(L))  if L[i][2] ]


def plot( ax, signals, t_final=None ):
  if t_final is None:
    #start by finding the maximum time
    t_final = get_t_final( signals )
    t_final *= 1.001

  channels = signals.items()
  channels.sort( lambda (k1,v1),(k2,v2): cmp(k2,k1) ) # reverse lexical sort

  ax.clear()
  labels = list()
  i = 0
  for c in channels:
    labels.append( c[0] )
    dt = mkdt( c[1], t_final )

    for g in c[1].items():
      ax.broken_barh(
        mkbbars( g[1], dt[ g[0] ] ), (i,1),
        facecolors=fc(i), linestyles=ls(g[0]), linewidth=2 )
    i += 1

  ax.set_xlabel('Time (s)')
  ax.set_yticks( np.r_[0.5:i] )
  ax.set_yticklabels(labels)
  pylab.setp(ax.get_xticklabels(), fontsize=8)
  pylab.setp(ax.get_yticklabels(), fontsize=8)
  ax.grid(True)
  return t_final


# This should be conformant to the output that the arbwave.Processor produces.
#
# in the following signals, it is expected that the last transition will be
# honored and that generally the voltage will remain at the given level after
# the signal is finished
#
# format:
#  'channel-label' : {
#    group-number : [(start-time, number-samples, value), ...],
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
    0 : [(0,1000,True), (100,100,False), (110,100,True), (120,100,False)],
    2 : [(130,35,True), (200,100,False)],
    3 : [(220,1,True)],
  },
  'CH1' : {
    0 : [(0,500,True), (50,300,False), (80,200,True), (100,1000,False)],
    2 : [(200,50,True), (210,25,False)],
    3 : [(215,50,True), (220,1,False)],
  },
  'CH2' : {
    0 : [(0,500,True), (50,300,False), (80,200,True), (100,1000,False)],
    2 : [(200,50,True), (210,1,False)],
  },
  'CH3' : {
    0 : [(10,300,True), (40,500,False), (90,100,True), (100,1000,False)],
    2 : [(200,50,True), (210,1,False)],
  },
  'CH4' : {
    0 : [(20,400,True), (60,300,False), (90,100,True), (110,900,False)],
    2 : [(200,50,True), (210,1,False)],
  },
  'CH5' : {
    0 : [(0,500,True), (50,300,False), (80,200,True), (100,1000,False)],
    2 : [(200,50,True), (210,1,False)],
  },
  'CH6' : {
    0 : [(0,1000,True), (100,100,False), (110,100,True), (120,100,False)],
    2 : [(130,350,True), (200,1,False)],
  },
  'CH7' : {
    0 : [(0,1000,True), (100,100,False), (110,100,True), (120,100,False)],
    2 : [(130,350,True), (200,1,False)],
  },
  'CH8' : {
    0 : [(0,1000,True), (100,100,False), (110,100,True), (120,100,False)],
    2 : [(130,350,True), (200,1,False)],
  },
}


if __name__ == '__main__':
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot( ax, example_signals )
  plt.show()
