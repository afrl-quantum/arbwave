# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting analog signals
"""
import numpy as np
import copy

def get_linestyle( group_number ):
  linestyles = [
    'solid',
    'dashed',
    'dashdot',
    'dotted',
    #(offset, on-off-dash-seq)
  ]
  return linestyles[ group_number % len(linestyles) ]


def get_marker( group_number ):
  markers = [
    'o', # circle marker
    'v', # triangle_down marker
    '^', # triangle_up marker
    '<', # triangle_left marker
    '>', # triangle_right marker
    '1', # tri_down marker
    '2', # tri_up marker
    '3', # tri_left marker
    '4', # tri_right marker
    's', # square marker
    'p', # pentagon marker
    '*', # star marker
    'h', # hexagon1 marker
    'H', # hexagon2 marker
    '+', # plus marker
    'x', # x marker
    'D', # diamond marker
    'd', # thin_diamond marker
  ]
  return markers[ group_number % len(markers) ]


def get_face_color( channel_number ):
  colors = [
    'red', 'brown', 'green', 'blue', 'black', 'orange', 'purple',
  ]
  return colors[ channel_number % len(colors) ]


def get_t_final( signals ):
  t_final = 0.0
  for c in signals.values():
    t_final = max( t_final, c.values()[-1][-1][0] )
  return t_final


def mkdt( signal, t_final ):
  dt = copy.deepcopy( signal )

  #append the first item of the next grouping
  items = signal.items()
  for i in xrange(1,len(items)):
    dt[ items[i-1][0] ].append( items[i][1][0] )
  #append a pseudo-item for the last grouping time length
  dt[ items[-1][0] ].append( (t_final, None) )

  for i in dt:
    dt[i] = np.diff( np.array(dt[i])[:,0] )
  return dt
