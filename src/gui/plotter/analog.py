# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting analog signals
"""
import pylab

import numpy as np
from common import *

fc=get_face_color
ls=get_linestyle


def mkxy( L, dt, Vi ):
  assert len(L) == len(dt), 'analog plot:  dt length calculated incorrectly'
  x = list()
  y = list()
  for i in xrange(len(L)):
    # L[i] : [ <start_time>, <number-of-samples>, <value> ]
    # dt[i]: <duration of ith sequence, in (s) >

    if Vi is None:
      x.append( L[i][0] )
      y.append( L[i][2] )
    else:
      x += [ L[i][0], L[i][0] ]
      y += [ Vi, L[i][2] ]
    Vi = L[i][2]

    # sub_dt = float(dt[i]) / L[i][1]

    # ti = L[i][0]
    # tf = (L[i][0]+dt[i])
    # # the -.5*sub_dt is to ensure that precision problems don't make us include
    # # the end point
    # x += list(np.arange( ti, (tf-0.5*sub_dt), sub_dt ))
    # y += list( np.ones( L[i][1] ) * L[i][2] )
  return x, y


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

    x = list()
    y = list()
    Vi = None
    for g in c[1].items():
      xg, yg = mkxy( g[1], dt[ g[0] ], Vi )
      Vi = yg[-1]
      x += xg
      y += yg
      s = max(1, int(.05 * len(xg)))
      #ax.plot( np.array(xg)[::s], np.array(yg)[::s], get_marker(g[0]), color=fc(i) )
    # By definition, each final transition is supposed to be honored as a fixed
    # value.  This final data point just ensures that this hold is plotted for
    # each channel until all channels have finished.
    x.append( t_final )
    y.append( y[-1] )

    ax.plot( x, y, color=fc(i), linewidth=2 )
    i += 1

  #ax.set_xlabel('Time (s)')
  #ax.set_yticks( np.r_[0.5:i] )
  #ax.set_yticklabels(labels)
  #ax.legend( labels, loc=(-0.25,0) )
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
    0 : [(0,1000,0.0), (90,100,0.1), (100,100,0.2), (110,100,0.3), (120,100,0.4)],
    2 : [(130,35,0.5), (200,100,.3)],
    3 : [(201,10,0.4), (202,10,0.5), (203,10,0.6), (204,10,0.7), (205,10,0.8),
         (206,10,0.9), (207,10,1.0), (208,10,0.9), (209,10,0.8), (210,10,0.7),
         (211,10,0.6), (212,10,0.5), (213,10,0.4), (214,10,0.3), (215,1,0.2)],
  },
  'CH1' : {
    0 : [(0,500,0.4),  (25,20,0.45), (50,300,0.5), (65,100,0.45), (80,200,0.3),
         (100,1000,0.45)],
    2 : [ (200.0, 10.0, -0.0873), (200.5, 10.0, -0.0532), (201.0, 10.0, -0.0061),
          (201.5, 10.0,  0.0424), (202.0, 10.0,  0.0806), (202.5, 10.0,  0.0991),
          (203.0, 10.0,  0.0933), (203.5, 10.0,  0.0646), (204.0, 10.0,  0.0202),
          (204.5, 10.0, -0.0292), (205.0, 10.0, -0.0714), (205.5, 10.0, -0.0962),
          (206.0, 10.0, -0.0974), (206.5, 10.0, -0.0748), (207.0, 10.0, -0.0338),
          (207.5, 10.0,  0.0154), (208.0, 10.0,  0.0609), (208.5, 10.0,  0.0914),
          (209.0, 10.0,  0.0996), (209.5, 10.0,  0.0834), ],
    3 : [(215,50,0.5), (220,1,0.4)],
  },
  'CH2' : {
    4 : [(0.0,10.0, 0.000), (0.5,10.0, 0.025), (1.0,10.0, 0.050),
         (1.5,10.0, 0.075), (2.0,10.0, 0.099), (2.5,10.0, 0.124),
         (3.0,10.0, 0.148), (3.5,10.0, 0.171), (4.0,10.0, 0.195),
         (4.5,10.0, 0.217), (5.0,10.0, 0.240), (5.5,10.0, 0.261),
         (6.0,10.0, 0.282), (6.5,10.0, 0.303), (7.0,10.0, 0.322),
         (7.5,10.0, 0.341), (8.0,10.0, 0.359), (8.5,10.0, 0.376),
         (9.0,10.0, 0.392), (9.5,10.0, 0.407), (10.0,10.0, 0.421),
         (10.5,10.0, 0.434), (11.0,10.0, 0.446), (11.5,10.0, 0.456),
         (12.0,10.0, 0.466), (12.5,10.0, 0.474), (13.0,10.0, 0.482),
         (13.5,10.0, 0.488), (14.0,10.0, 0.493), (14.5,10.0, 0.496),
         (15.0,10.0, 0.499), (15.5,10.0, 0.500), (16.0,10.0, 0.500),
         (16.5,10.0, 0.498), (17.0,10.0, 0.496), (17.5,10.0, 0.492),
         (18.0,10.0, 0.487), (18.5,10.0, 0.481), (19.0,10.0, 0.473),
         (19.5,10.0, 0.464), (20.0,10.0, 0.455), (20.5,10.0, 0.444),
         (21.0,10.0, 0.432), (21.5,10.0, 0.418), (22.0,10.0, 0.404),
         (22.5,10.0, 0.389), (23.0,10.0, 0.373), (23.5,10.0, 0.356),
         (24.0,10.0, 0.338), (24.5,10.0, 0.319), (25.0,10.0, 0.299),
         (25.5,10.0, 0.279), (26.0,10.0, 0.258), (26.5,10.0, 0.236),
         (27.0,10.0, 0.214), (27.5,10.0, 0.191), (28.0,10.0, 0.167),
         (28.5,10.0, 0.144), (29.0,10.0, 0.120), (29.5,10.0, 0.095),
         (30.0,10.0, 0.071), (30.5,10.0, 0.046), (31.0,10.0, 0.021),
         (31.5,10.0,-0.004), (32.0,10.0,-0.029), (32.5,10.0,-0.054),
         (33.0,10.0,-0.079), (33.5,10.0,-0.103), (34.0,10.0,-0.128),
         (34.5,10.0,-0.152), (35.0,10.0,-0.175), (35.5,10.0,-0.199),
         (36.0,10.0,-0.221), (36.5,10.0,-0.243), (37.0,10.0,-0.265),
         (37.5,10.0,-0.286), (38.0,10.0,-0.306), (38.5,10.0,-0.325),
         (39.0,10.0,-0.344), (39.5,10.0,-0.362), (40.0,10.0,-0.378),
         (40.5,10.0,-0.394), (41.0,10.0,-0.409), (41.5,10.0,-0.423),
         (42.0,10.0,-0.436), (42.5,10.0,-0.447), (43.0,10.0,-0.458),
         (43.5,10.0,-0.468), (44.0,10.0,-0.476), (44.5,10.0,-0.483),
         (45.0,10.0,-0.489), (45.5,10.0,-0.493), (46.0,10.0,-0.497),
         (46.5,10.0,-0.499), (47.0,10.0,-0.500), (47.5,10.0,-0.500),
         (48.0,10.0,-0.498), (48.5,10.0,-0.495), (49.0,10.0,-0.491),
         (49.5,10.0,-0.486), (50.0,10.0,-0.479), (50.5,10.0,-0.472),
         (51.0,10.0,-0.463), (51.5,10.0,-0.453), (52.0,10.0,-0.442),
         (52.5,10.0,-0.429), (53.0,10.0,-0.416), (53.5,10.0,-0.402),
         (54.0,10.0,-0.386), (54.5,10.0,-0.370), (55.0,10.0,-0.353),
         (55.5,10.0,-0.335), (56.0,10.0,-0.316), (56.5,10.0,-0.296),
         (57.0,10.0,-0.275), (57.5,10.0,-0.254), (58.0,10.0,-0.232),
         (58.5,10.0,-0.210), (59.0,10.0,-0.187), (59.5,10.0,-0.164),
         (60.0,10.0,-0.140), (60.5,10.0,-0.116), (61.0,10.0,-0.091),
         (61.5,10.0,-0.066), (62.0,10.0,-0.042), (62.5,10.0,-0.017),
         (63.0,10.0, 0.008), (63.5,10.0, 0.033), (64.0,10.0, 0.058),
         (64.5,10.0, 0.083), (65.0,10.0, 0.108), (65.5,10.0, 0.132),
         (66.0,10.0, 0.156), (66.5,10.0, 0.179), (67.0,10.0, 0.202),
         (67.5,10.0, 0.225), (68.0,10.0, 0.247), (68.5,10.0, 0.268),
         (69.0,10.0, 0.289), (69.5,10.0, 0.309), (70.0,10.0, 0.328),
         (70.5,10.0, 0.347), (71.0,10.0, 0.364), (71.5,10.0, 0.381),
         (72.0,10.0, 0.397), (72.5,10.0, 0.412), (73.0,10.0, 0.425),
         (73.5,10.0, 0.438), (74.0,10.0, 0.449), (74.5,10.0, 0.460),
         (75.0,10.0, 0.469), (75.5,10.0, 0.477), (76.0,10.0, 0.484),
         (76.5,10.0, 0.490), (77.0,10.0, 0.494), (77.5,10.0, 0.497),
         (78.0,10.0, 0.499), (78.5,10.0, 0.500), (79.0,10.0, 0.499),
         (79.5,10.0, 0.498), (80.0,10.0, 0.495), (80.5,10.0, 0.490),
         (81.0,10.0, 0.485), (81.5,10.0, 0.478), (82.0,10.0, 0.470),
         (82.5,10.0, 0.461), (83.0,10.0, 0.451), (83.5,10.0, 0.440),
         (84.0,10.0, 0.427), (84.5,10.0, 0.414), (85.0,10.0, 0.399),
         (85.5,10.0, 0.384), (86.0,10.0, 0.367), (86.5,10.0, 0.350),
         (87.0,10.0, 0.331), (87.5,10.0, 0.312), (88.0,10.0, 0.292),
         (88.5,10.0, 0.272), (89.0,10.0, 0.251), (89.5,10.0, 0.229),
         (90.0,10.0, 0.206), (90.5,10.0, 0.183), (91.0,10.0, 0.160),
         (91.5,10.0, 0.136), (92.0,10.0, 0.111), (92.5,10.0, 0.087),
         (93.0,10.0, 0.062), (93.5,10.0, 0.037), (94.0,10.0, 0.012),
         (94.5,10.0,-0.013), (95.0,10.0,-0.038), (95.5,10.0,-0.062),
         (96.0,10.0,-0.087), (96.5,10.0,-0.112), (97.0,10.0,-0.136),
         (97.5,10.0,-0.160), (98.0,10.0,-0.183), (98.5,10.0,-0.206),
         (99.0,10.0,-0.229), (99.5,10.0,-0.251), (100.0,10.0,-0.272),
         (100.5,10.0,-0.293), (101.0,10.0,-0.313), (101.5,10.0,-0.332),
         (102.0,10.0,-0.350), (102.5,10.0,-0.367), (103.0,10.0,-0.384),
         (103.5,10.0,-0.399), (104.0,10.0,-0.414), (104.5,10.0,-0.427),
         (105.0,10.0,-0.440), (105.5,10.0,-0.451), (106.0,10.0,-0.461),
         (106.5,10.0,-0.470), (107.0,10.0,-0.478), (107.5,10.0,-0.485),
         (108.0,10.0,-0.490), (108.5,10.0,-0.495), (109.0,10.0,-0.498),
         (109.5,10.0,-0.499), (110.0,10.0,-0.500), (110.5,10.0,-0.499),
         (111.0,10.0,-0.497), (111.5,10.0,-0.494), (112.0,10.0,-0.490),
         (112.5,10.0,-0.484), (113.0,10.0,-0.477), (113.5,10.0,-0.469),
         (114.0,10.0,-0.460), (114.5,10.0,-0.449), (115.0,10.0,-0.438),
         (115.5,10.0,-0.425), (116.0,10.0,-0.411), (116.5,10.0,-0.397),
         (117.0,10.0,-0.381), (117.5,10.0,-0.364), (118.0,10.0,-0.347),
         (118.5,10.0,-0.328), (119.0,10.0,-0.309), (119.5,10.0,-0.289),
         (120.0,10.0,-0.268), (120.5,10.0,-0.247), (121.0,10.0,-0.225),
         (121.5,10.0,-0.202), (122.0,10.0,-0.179), (122.5,10.0,-0.156),
         (123.0,10.0,-0.132), (123.5,10.0,-0.107), (124.0,10.0,-0.083),
         (124.5,10.0,-0.058), (125.0,10.0,-0.033), (125.5,10.0,-0.008),
         (126.0,10.0, 0.017), (126.5,10.0, 0.042), (127.0,10.0, 0.067),
         (127.5,10.0, 0.091), (128.0,10.0, 0.116), (128.5,10.0, 0.140),
         (129.0,10.0, 0.164), (129.5,10.0, 0.187), (130.0,10.0, 0.210),
         (130.5,10.0, 0.232), (131.0,10.0, 0.254), (131.5,10.0, 0.276),
         (132.0,10.0, 0.296), (132.5,10.0, 0.316), (133.0,10.0, 0.335),
         (133.5,10.0, 0.353), (134.0,10.0, 0.370), (134.5,10.0, 0.387),
         (135.0,10.0, 0.402), (135.5,10.0, 0.416), (136.0,10.0, 0.430),
         (136.5,10.0, 0.442), (137.0,10.0, 0.453), (137.5,10.0, 0.463),
         (138.0,10.0, 0.472), (138.5,10.0, 0.480), (139.0,10.0, 0.486),
         (139.5,10.0, 0.491), (140.0,10.0, 0.495), (140.5,10.0, 0.498),
         (141.0,10.0, 0.500), (141.5,10.0, 0.500), (142.0,10.0, 0.499),
         (142.5,10.0, 0.497), (143.0,10.0, 0.493), (143.5,10.0, 0.489),
         (144.0,10.0, 0.483), (144.5,10.0, 0.476), (145.0,10.0, 0.467),
         (145.5,10.0, 0.458), (146.0,10.0, 0.447), (146.5,10.0, 0.436),
         (147.0,10.0, 0.423), (147.5,10.0, 0.409), (148.0,10.0, 0.394),
         (148.5,10.0, 0.378), (149.0,10.0, 0.361), (149.5,10.0, 0.344),
         (150.0,10.0, 0.325), (150.5,10.0, 0.306), (151.0,10.0, 0.286),
         (151.5,10.0, 0.265), (152.0,10.0, 0.243), (152.5,10.0, 0.221),
         (153.0,10.0, 0.198), (153.5,10.0, 0.175), (154.0,10.0, 0.152),
         (154.5,10.0, 0.128), (155.0,10.0, 0.103), (155.5,10.0, 0.079),
         (156.0,10.0, 0.054), (156.5,10.0, 0.029), (157.0,10.0, 0.004),
         (157.5,10.0,-0.021), (158.0,10.0,-0.046), (158.5,10.0,-0.071),
         (159.0,10.0,-0.095), (159.5,10.0,-0.120), (160.0,10.0,-0.144),
         (160.5,10.0,-0.168), (161.0,10.0,-0.191), (161.5,10.0,-0.214),
         (162.0,10.0,-0.236), (162.5,10.0,-0.258), (163.0,10.0,-0.279),
         (163.5,10.0,-0.299), (164.0,10.0,-0.319), (164.5,10.0,-0.338),
         (165.0,10.0,-0.356), (165.5,10.0,-0.373), (166.0,10.0,-0.389),
         (166.5,10.0,-0.404), (167.0,10.0,-0.419), (167.5,10.0,-0.432),
         (168.0,10.0,-0.444), (168.5,10.0,-0.455), (169.0,10.0,-0.465),
         (169.5,10.0,-0.473), (170.0,10.0,-0.481), (170.5,10.0,-0.487),
         (171.0,10.0,-0.492), (171.5,10.0,-0.496), (172.0,10.0,-0.498),
         (172.5,10.0,-0.500), (173.0,10.0,-0.500), (173.5,10.0,-0.499),
         (174.0,10.0,-0.496), (174.5,10.0,-0.493), (175.0,10.0,-0.488),
         (175.5,10.0,-0.482), (176.0,10.0,-0.474), (176.5,10.0,-0.466),
         (177.0,10.0,-0.456), (177.5,10.0,-0.446), (178.0,10.0,-0.434),
         (178.5,10.0,-0.421), (179.0,10.0,-0.407), (179.5,10.0,-0.392),
         (180.0,10.0,-0.375), (180.5,10.0,-0.359), (181.0,10.0,-0.341),
         (181.5,10.0,-0.322), (182.0,10.0,-0.302), (182.5,10.0,-0.282),
         (183.0,10.0,-0.261), (183.5,10.0,-0.240), (184.0,10.0,-0.217),
         (184.5,10.0,-0.195), (185.0,10.0,-0.171), (185.5,10.0,-0.148),
         (186.0,10.0,-0.123), (186.5,10.0,-0.099), (187.0,10.0,-0.074),
         (187.5,10.0,-0.050), (188.0,10.0,-0.025), (188.5,10.0, 0.000),
         (189.0,10.0, 0.025), (189.5,10.0, 0.050), (190.0,10.0, 0.075),
         (190.5,10.0, 0.100), (191.0,10.0, 0.124), (191.5,10.0, 0.148),
         (192.0,10.0, 0.172), (192.5,10.0, 0.195), (193.0,10.0, 0.218),
         (193.5,10.0, 0.240), (194.0,10.0, 0.262), (194.5,10.0, 0.283),
         (195.0,10.0, 0.303), (195.5,10.0, 0.322), (196.0,10.0, 0.341),
         (196.5,10.0, 0.359), (197.0,10.0, 0.376), (197.5,10.0, 0.392),
         (198.0,10.0, 0.407), (198.5,10.0, 0.421), (199.0,10.0, 0.434),
         (199.5,10.0, 0.446), (200.0,10.0, 0.456), (200.5,10.0, 0.466),
         (201.0,10.0, 0.475), (201.5,10.0, 0.482), (202.0,10.0, 0.488),
         (202.5,10.0, 0.493), (203.0,10.0, 0.496), (203.5,10.0, 0.499),
         (204.0,10.0, 0.500), (204.5,10.0, 0.500), (205.0,10.0, 0.498),
         (205.5,10.0, 0.496), (206.0,10.0, 0.492), (206.5,10.0, 0.487),
         (207.0,10.0, 0.481), (207.5,10.0, 0.473), (208.0,10.0, 0.464),
         (208.5,10.0, 0.455), (209.0,10.0, 0.444), (209.5,10.0, 0.431)],
  },
}


if __name__ == '__main__':
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot( ax, example_signals )
  plt.show()