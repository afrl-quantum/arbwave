# vim: ts=2:sw=2:tw=80:nowrap
"""
Utilities for plotting digital signals
"""
import numpy as np

# broken_barh( xranges, yrange, **kwargs )
#  xranges : sequence of (xmin, xwidth)
#  yrange  : sequence of (ymin, ywidth)

def get_linestyle( group_number ):
  linestyles = [
    'solid',
    'dashed',
    'dashdot',
    'dotted',
    #(offset, on-off-dash-seq)
  ]
  return linestyles[ group_number % len(linestyles) ]

def get_face_color( channel_number ):
  colors = [
    'red', 'brown', 'green', 'blue', 'black', 'orange', 'purple',
  ]
  return colors[ channel_number % len(colors) ]


fc=get_face_color
ls=get_linestyle

def sigdict_to_list( sigs, grange, endpad ):
  dt = np.append( np.diff( sigs[:,0] ), endpad )
  return [ (sigs[i][0], dt[i])  for i in xrange(*grange)  if sigs[i][1] ]

def plot( ax, signals, end_padding=1 ):
  """
    end_padding : how much to pad the end of the signal with in order to
                  satisfy the demand that end-transitions be honored
  """
  channels = signals['channels'].items()
  channels.sort( lambda (k1,v1),(k2,v2): cmp(k2,k1) ) # reverse lexical sort
  dt = signals['dt']

  max_x = 0.0
  labels = list()
  i = 0
  for c in channels:
    labels.append( c[0] )
    sigs = c[1]['signal'].items()
    sigs.sort( lambda (k1,v1),(k2,v2): cmp(k1,k2) ) # sort numerically
    for g in c[1]['groups'].items():
      bbars = sigdict_to_list( np.array(sigs), g[0], dt[g[1]]*end_padding )
      max_x = max( max_x, bbars[-1][0]+bbars[-1][1] )
      ax.broken_barh(
        bbars, (i,1),
        facecolors=fc(i), linestyles=ls(g[1]), linewidth=2 )
    i += 1

  ax.set_xlabel('Time (s)')
  ax.set_yticks( np.r_[0.5:i] )
  ax.set_yticklabels(labels)
  ax.grid(True)
  return max_x


# This should be conformant to the output that the arbwave.Processor produces.
#
# in the following signals, it is expected that the last transition will be
# honored and that generally the voltage will remain at the given level after
# the signal is finished
example_signals = {
  'dt' : { 0:.1, 1:.1, 2:.2, 3:.1 },
  'channels' : {
    'CH0' : {
      'signal' :{0:True, 100:False, 110:True, 120:False, 130:True, 200:False, 220:True},
      'groups' :{(0,4):0, (4,6):2, (6,7):3},
    },
    'CH1' : {
      'signal' :{0:True, 50:False, 80:True, 100:False, 200:True, 210:False, 215:True, 220:False},
      'groups' :{(0,4):0, (4,6):2, (6,8):3},
    },
    'CH2' : {
      'signal' :{0:True, 50:False, 80:True, 100:False, 200:True, 210:False},
      'groups' :{(0,4):0, (4,6):2},
    },
    'CH3' : {
      'signal' :{10:True, 40:False, 90:True, 100:False, 200:True, 210:False},
      'groups' :{(0,4):0, (4,6):2},
    },
    'CH4' : {
      'signal' :{20:True, 60:False, 90:True, 110:False, 200:True, 210:False},
      'groups' :{(0,4):0, (4,6):2},
    },
    'CH5' : {
      'signal' :{0:True, 50:False, 80:True, 100:False, 200:True, 210:False},
      'groups' :{(0,4):0, (4,6):2},
    },
    'CH6' : {
      'signal' :{0:True, 100:False, 110:True, 120:False, 130:True, 200:False},
      'groups' :{(0,4):0, (4,6):2},
    },
    'CH7' : {
      'signal' :{0:True, 100:False, 110:True, 120:False, 130:True, 200:False},
      'groups' :{(0,4):0, (4,6):2},
    },
    'CH8' : {
      'signal' :{0:True, 100:False, 110:True, 120:False, 130:True, 200:False},
      'groups' :{(0,4):0, (4,6):2},
    },
  },
}


if __name__ == '__main__':
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plot( ax, example_signals )
  plt.show()
