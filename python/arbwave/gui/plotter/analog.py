# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting analog signals
"""
from matplotlib.colors import ColorConverter

import numpy as np
from .common import *

fc=get_face_color
ls=get_linestyle


def mkxy(encoding, L, x0, y0):
  """
  Convert the grouping data into (x,y) points for various types of transitions.
  encoding : Specifies the type of output to create:
    'linear' : allows the output to linearly ramp from one value to another
    'step'   : each output remains fixed until a subsequent transition
    'bezier' : (speculated, not supported)
  L :  [(start-time, value), ...]
       for each grouping of channel data (see below).
  x0:  x-value for last value y0.  If x0 is None, this is the first value
       grouping for this channel.
  y0:  Previous value for a channel.  If y0 is None, this is the first value
       grouping for this channel.
  """
  if encoding == 'linear':
    X, Y = list(zip(*L))
    if y0 is not None:
      # if this is not the first point, we copy the last value for our new first
      # time to ensure that a 'step' from a previous grouping remains a step
      x = np.r_[x0, float(X[0]), np.array(X, dtype=float)]
      y = np.r_[y0,   y0, np.array(Y, dtype=float)] # remove units
    else:
      x = np.array(X, dtype=float)
      y = np.array(Y, dtype=float)
    x0 = x[-1]
    y0 = y[-1]
  else:
    # take care of beginning first
    if y0 is None:
      istart = 1
      x = np.zeros(2* (len(L) - 1) + 1)
      y = np.zeros(2* (len(L) - 1) + 1)
      x[0] = x0 = float(L[0][0]) # remove units
      y[0] = y0 = float(L[0][1]) # remove units
    else:
      # this group of (xi,yi) is not the beginning for the channel
      istart = 0
      x = np.zeros(2* len(L) + 1)
      y = np.zeros(2* len(L) + 1)
      x[0] = x0
      y[0] = y0

    # loop through the rest
    for i, (l0, l1) in zip(range(1, 2*len(L) + 1, 2), L[istart:]):
      x[i:i+2] = [ float(l0), float(l0) ]
      y[i:i+2] = [ float(y0), float(l1) ] # remove units
      x0, y0 = l0, float(l1)
  return x, y, x0, y0


def plot( ax, signals, name_map=None, t_final=None ):
  if t_final is None:
    #start by finding the maximum time
    t_final = get_t_final( signals )
    t_final *= 1.001

  channels = list(signals.items())
  if name_map:
    channels.sort( key = lambda v: -name_map[v[0]]['order'] )
    get_label  = lambda n : name_map[n]['name']
    get_xscale = lambda n : float(name_map[n]['dt_clk']) #strip units
    get_yscale = lambda n : name_map[n]['yscale']
  else:
    channels.sort( key = lambda v: v[0] ) # reverse lexical sort
    get_label  = lambda n : n
    get_xscale = lambda n : 1.0 # scaled by unity by default
    # offset by 0.0 and scaled by unity by default:
    get_yscale = lambda n : (0.0, 1.0)

  def apply_yscale(y, yscale):
    """
    Given an array of values y, where y is a subset of Y, we need to apply a
    scaling like:
      y = (y - min(Y)) / (max(Y) - min(Y))
    """
    if yscale[0] != 0:   # 'if' is so we can avoid looping if not necessary
      y -= yscale[0]
    if yscale[1] != 1.0: # 'if' is so we can avoid looping if not necessary
      y *= yscale[1]
    return y


  cconv = ColorConverter()

  ax.clear()
  labels = list()
  i = 0
  group_lines = dict()
  ylim = 1e300, 1e-300
  for chname, grp_data in channels:
    labels.append( get_label( chname ) )
    xscale = get_xscale( chname )
    yscale = get_yscale( chname )

    x0 = None
    y0 = None
    # sort groups by time in last (time,value) element
    groups = sorted(grp_data.items(),
                    key = lambda grp_encdata : grp_encdata[1][1][-1][0])
    for grp, (encoding, data) in groups:
      xg, yg, x0, y0 = mkxy(encoding, data, x0, y0)
      xg *= xscale
      apply_yscale(yg, yscale)

      ylim = min(ylim[0], yg.min()), max(ylim[1], yg.max())

      group_lines[(grp,chname)] = ax.plot(xg, yg, color=fc(i), linewidth=2)[0]

    # By definition, each final transition is supposed to be honored as a fixed
    # value.  This final data point just ensures that this hold is plotted for
    # each channel until all channels have finished.
    x0 *= xscale
    y0 = apply_yscale(y0, yscale)
    x1 = t_final
    y1 = y0

    group_lines[((-1,), chname)] = \
      ax.plot( [x0, x1], [y0, y1], color=fc(i), linewidth=2 )[0]
    i += 1

  #ax.set_xlabel('Time (s)')
  #ax.set_yticks( np.r_[0.5:i] )
  #ax.set_yticklabels(labels)
  #ax.legend( labels, loc=(-0.25,0) )
  dy = (ylim[1] - ylim[0]) * .1
  ax.set_ylim( float(ylim[0]-dy), float(ylim[1]+dy) )
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
# group should be interpreted.  See mkxy above for the list of possible
# encodings.
#
# The start-time is normally in integer number of clock cycles
example_signals = {
  'CH0' : {
    0 : ('step', [(0,0.0), (900,0.0)]),
    1 : ('linear', [(901,0.0), (1299,0.5)]),
    2 : ('step', [(1300,0.5), (2000,.3)]),
    3 : ('step', [(2010,0.4), (2020,0.5), (2030,0.6), (2040,0.7), (2050,0.8),
                  (2060,0.9), (2070,1.0), (2080,0.9), (2090,0.8), (2100,0.7),
                  (2110,0.6), (2120,0.5), (2130,0.4), (2140,0.3), (2150,0.2)]),
  },
  'CH1' : {
    0 : ('step', [(0,0.4),  (250,0.45), (500,0.5), (650,0.45), (800,0.3), (1000,0.45)]),
    2 : ('step', [ (2000, -0.0873), (2005, -0.0532), (2010, -0.0061),
                   (2015,  0.0424), (2020,  0.0806), (2025,  0.0991),
                   (2030,  0.0933), (2035,  0.0646), (2040,  0.0202),
                   (2045, -0.0292), (2050, -0.0714), (2055, -0.0962),
                   (2060, -0.0974), (2065, -0.0748), (2070, -0.0338),
                   (2075,  0.0154), (2080,  0.0609), (2085,  0.0914),
                   (2090,  0.0996), (2095,  0.0834), ]),
    3 : ('step', [(2150,0.5), (2200,0.4)]),
  },
  'CH2' : {
    4 : ('step', [(0, 0.000),  (5,  0.025), (10, 0.050),
                  (15, 0.075), (20, 0.099), (25, 0.124),
                  (30, 0.148), (35, 0.171), (40, 0.195),
                  (45, 0.217), (50, 0.240), (55, 0.261),
                  (60, 0.282), (65, 0.303), (70, 0.322),
                  (75, 0.341), (80, 0.359), (85, 0.376),
                  (90, 0.392), (95, 0.407), (100, 0.421),
                  (105, 0.434), (110, 0.446), (115, 0.456),
                  (120, 0.466), (125, 0.474), (130, 0.482),
                  (135, 0.488), (140, 0.493), (145, 0.496),
                  (150, 0.499), (155, 0.500), (160, 0.500),
                  (165, 0.498), (170, 0.496), (175, 0.492),
                  (180, 0.487), (185, 0.481), (190, 0.473),
                  (195, 0.464), (200, 0.455), (205, 0.444),
                  (210, 0.432), (215, 0.418), (220, 0.404),
                  (225, 0.389), (230, 0.373), (235, 0.356),
                  (240, 0.338), (245, 0.319), (250, 0.299),
                  (255, 0.279), (260, 0.258), (265, 0.236),
                  (270, 0.214), (275, 0.191), (280, 0.167),
                  (285, 0.144), (290, 0.120), (295, 0.095),
                  (300, 0.071), (305, 0.046), (310, 0.021),
                  (315,-0.004), (320,-0.029), (325,-0.054),
                  (330,-0.079), (335,-0.103), (340,-0.128),
                  (345,-0.152), (350,-0.175), (355,-0.199),
                  (360,-0.221), (365,-0.243), (370,-0.265),
                  (375,-0.286), (380,-0.306), (385,-0.325),
                  (390,-0.344), (395,-0.362), (400,-0.378),
                  (405,-0.394), (410,-0.409), (415,-0.423),
                  (420,-0.436), (425,-0.447), (430,-0.458),
                  (435,-0.468), (440,-0.476), (445,-0.483),
                  (450,-0.489), (455,-0.493), (460,-0.497),
                  (465,-0.499), (470,-0.500), (475,-0.500),
                  (480,-0.498), (485,-0.495), (490,-0.491),
                  (495,-0.486), (500,-0.479), (505,-0.472),
                  (510,-0.463), (515,-0.453), (520,-0.442),
                  (525,-0.429), (530,-0.416), (535,-0.402),
                  (540,-0.386), (545,-0.370), (550,-0.353),
                  (555,-0.335), (560,-0.316), (565,-0.296),
                  (570,-0.275), (575,-0.254), (580,-0.232),
                  (585,-0.210), (590,-0.187), (595,-0.164),
                  (600,-0.140), (605,-0.116), (610,-0.091),
                  (615,-0.066), (620,-0.042), (625,-0.017),
                  (630, 0.008), (635, 0.033), (640, 0.058),
                  (645, 0.083), (650, 0.108), (655, 0.132),
                  (660, 0.156), (665, 0.179), (670, 0.202),
                  (675, 0.225), (680, 0.247), (685, 0.268),
                  (690, 0.289), (695, 0.309), (700, 0.328),
                  (705, 0.347), (710, 0.364), (715, 0.381),
                  (720, 0.397), (725, 0.412), (730, 0.425),
                  (735, 0.438), (740, 0.449), (745, 0.460),
                  (750, 0.469), (755, 0.477), (760, 0.484),
                  (765, 0.490), (770, 0.494), (775, 0.497),
                  (780, 0.499), (785, 0.500), (790, 0.499),
                  (795, 0.498), (800, 0.495), (805, 0.490),
                  (810, 0.485), (815, 0.478), (820, 0.470),
                  (825, 0.461), (830, 0.451), (835, 0.440),
                  (840, 0.427), (845, 0.414), (850, 0.399),
                  (855, 0.384), (860, 0.367), (865, 0.350),
                  (870, 0.331), (875, 0.312), (880, 0.292),
                  (885, 0.272), (890, 0.251), (895, 0.229),
                  (900, 0.206), (905, 0.183), (910, 0.160),
                  (915, 0.136), (920, 0.111), (925, 0.087),
                  (930, 0.062), (935, 0.037), (940, 0.012),
                  (945,-0.013), (950,-0.038), (955,-0.062),
                  (960,-0.087), (965,-0.112), (970,-0.136),
                  (975,-0.160), (980,-0.183), (985,-0.206),
                  (990,-0.229), (995,-0.251), (1000,-0.272),
                  (1005,-0.293), (1010,-0.313), (1015,-0.332),
                  (1020,-0.350), (1025,-0.367), (1030,-0.384),
                  (1035,-0.399), (1040,-0.414), (1045,-0.427),
                  (1050,-0.440), (1055,-0.451), (1060,-0.461),
                  (1065,-0.470), (1070,-0.478), (1075,-0.485),
                  (1080,-0.490), (1085,-0.495), (1090,-0.498),
                  (1095,-0.499), (1100,-0.500), (1105,-0.499),
                  (1110,-0.497), (1115,-0.494), (1120,-0.490),
                  (1125,-0.484), (1130,-0.477), (1135,-0.469),
                  (1140,-0.460), (1145,-0.449), (1150,-0.438),
                  (1155,-0.425), (1160,-0.411), (1165,-0.397),
                  (1170,-0.381), (1175,-0.364), (1180,-0.347),
                  (1185,-0.328), (1190,-0.309), (1195,-0.289),
                  (1200,-0.268), (1205,-0.247), (1210,-0.225),
                  (1215,-0.202), (1220,-0.179), (1225,-0.156),
                  (1230,-0.132), (1235,-0.107), (1240,-0.083),
                  (1245,-0.058), (1250,-0.033), (1255,-0.008),
                  (1260, 0.017), (1265, 0.042), (1270, 0.067),
                  (1275, 0.091), (1280, 0.116), (1285, 0.140),
                  (1290, 0.164), (1295, 0.187), (1300, 0.210),
                  (1305, 0.232), (1310, 0.254), (1315, 0.276),
                  (1320, 0.296), (1325, 0.316), (1330, 0.335),
                  (1335, 0.353), (1340, 0.370), (1345, 0.387),
                  (1350, 0.402), (1355, 0.416), (1360, 0.430),
                  (1365, 0.442), (1370, 0.453), (1375, 0.463),
                  (1380, 0.472), (1385, 0.480), (1390, 0.486),
                  (1395, 0.491), (1400, 0.495), (1405, 0.498),
                  (1410, 0.500), (1415, 0.500), (1420, 0.499),
                  (1425, 0.497), (1430, 0.493), (1435, 0.489),
                  (1440, 0.483), (1445, 0.476), (1450, 0.467),
                  (1455, 0.458), (1460, 0.447), (1465, 0.436),
                  (1470, 0.423), (1475, 0.409), (1480, 0.394),
                  (1485, 0.378), (1490, 0.361), (1495, 0.344),
                  (1500, 0.325), (1505, 0.306), (1510, 0.286),
                  (1515, 0.265), (1520, 0.243), (1525, 0.221),
                  (1530, 0.198), (1535, 0.175), (1540, 0.152),
                  (1545, 0.128), (1550, 0.103), (1555, 0.079),
                  (1560, 0.054), (1565, 0.029), (1570, 0.004),
                  (1575,-0.021), (1580,-0.046), (1585,-0.071),
                  (1590,-0.095), (1595,-0.120), (1600,-0.144),
                  (1605,-0.168), (1610,-0.191), (1615,-0.214),
                  (1620,-0.236), (1625,-0.258), (1630,-0.279),
                  (1635,-0.299), (1640,-0.319), (1645,-0.338),
                  (1650,-0.356), (1655,-0.373), (1660,-0.389),
                  (1665,-0.404), (1670,-0.419), (1675,-0.432),
                  (1680,-0.444), (1685,-0.455), (1690,-0.465),
                  (1695,-0.473), (1700,-0.481), (1705,-0.487),
                  (1710,-0.492), (1715,-0.496), (1720,-0.498),
                  (1725,-0.500), (1730,-0.500), (1735,-0.499),
                  (1740,-0.496), (1745,-0.493), (1750,-0.488),
                  (1755,-0.482), (1760,-0.474), (1765,-0.466),
                  (1770,-0.456), (1775,-0.446), (1780,-0.434),
                  (1785,-0.421), (1790,-0.407), (1795,-0.392),
                  (1800,-0.375), (1805,-0.359), (1810,-0.341),
                  (1815,-0.322), (1820,-0.302), (1825,-0.282),
                  (1830,-0.261), (1835,-0.240), (1840,-0.217),
                  (1845,-0.195), (1850,-0.171), (1855,-0.148),
                  (1860,-0.123), (1865,-0.099), (1870,-0.074),
                  (1875,-0.050), (1880,-0.025), (1885, 0.000),
                  (1890, 0.025), (1895, 0.050), (1900, 0.075),
                  (1905, 0.100), (1910, 0.124), (1915, 0.148),
                  (1920, 0.172), (1925, 0.195), (1930, 0.218),
                  (1935, 0.240), (1940, 0.262), (1945, 0.283),
                  (1950, 0.303), (1955, 0.322), (1960, 0.341),
                  (1965, 0.359), (1970, 0.376), (1975, 0.392),
                  (1980, 0.407), (1985, 0.421), (1990, 0.434),
                  (1995, 0.446), (2000, 0.456), (2005, 0.466),
                  (2010, 0.475), (2015, 0.482), (2020, 0.488),
                  (2025, 0.493), (2030, 0.496), (2035, 0.499),
                  (2040, 0.500), (2045, 0.500), (2050, 0.498),
                  (2055, 0.496), (2060, 0.492), (2065, 0.487),
                  (2070, 0.481), (2075, 0.473), (2080, 0.464),
                  (2085, 0.455), (2090, 0.444), (2095, 0.431)]),
  },
}


def plot_test():
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot( ax, example_signals )
  plt.show()
