# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting analog signals
"""
import matplotlib
import numpy as np
import copy

font = {
#  'family' : 'monospace',
#  'weight' : 'extrabold',
  'size'   : 8,
}

matplotlib.rc('font', **font)
#matplotlib.rcParams.update({'font.size': 8})


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


highlight_linewidth = 3.0 #5.0
highlight_color = ''
highlight_alpha = 1.0

def get_face_color( channel_number ):
  colors = [
    (0., 0., 0., .6), #black
    (0., .5, 0., .6), #green
    (1., 0., 0., .6), #red
    (0., 1., 0., .6), #green
    (0., 0., 1., .6), #blue
    #(1.,1.,0.,.6), #yellow
    (1., .6, .2, .6),
    (.5, .6, 0., .6),
    (0., .5, .5, .6), # Teal
    (.5, 0., 1., .6),
    (1., 0., .5, .6),
    (.5, 0., .5, .6),
    (1., .4, 0., .6),
    (1., 0., 1., .6), #
  ]
  return colors[ channel_number % len(colors) ]


def get_t_final( signals ):
  """
  Determine the maximum time for the given set of signals.  This function is
  not used by Arbwave, but rather mostly serves to facilitate the dummy data at
  the bottom of analog.py and digital.py to be plotted.
  """
  t_final = 0.0
  for c in signals.values(): # for each channel's data
    L = c.items()
    L.sort( key = lambda i : i[0] )# sort by group number (i.e. path)
    t_final = max( t_final, L[-1][1][1][-1][0] )
  return t_final


def mkdt( signal, t_final ):
  dt = copy.deepcopy( signal )

  #append the first item of the next grouping
  items = signal.items()
  items.sort(key = lambda i : i[0]) # ensure that these are sorted by group/path
  for i in xrange(1,len(items)):
    dt[ items[i-1][0] ][1].append( items[i][1][1][0] )
  #append a pseudo-item for the last grouping time length
  dt[ items[-1][0] ][1].append( (t_final, None) )

  # here, we remove/ignore the (as yet unused) encoding
  for i in dt:
    dt[i] = np.diff( np.array(dt[i][1])[:,0] )
  return dt
