# vim: ts=2:sw=2:tw=80:nowrap

### BEGIN TEMPORARY CONFIG ###
channels = {
  'MOT Detuning' : {
    'device'  : '/dev0/ao0',
    'scaling' : 'min(10,max(-10,{value}/1.5))',
    'value'   : '10*300',
    'enabled' : True,
  },

  'MOT Power' : {
    'device'  : '/dev0/ao1',
    'scaling' : 'min(10,max(-10,{value}))',
    'value'   : '10*300',
    'enabled' : True,
  },

  'U Current' : {
    'device'  : '/dev0/ao2',
    'scaling' : 'min(10,max(-10,{value}))',
    'value'   : '10*300',
    'enabled' : True,
  },

  'Z Current' : {
    'device'  : '/dev0/ao3',
    'scaling' : 'min(10,max(-10,{value}))',
    'value'   : '10*300',
    'enabled' : True,
  },
}

waveforms =  [
  { 'group-label' : 'MOT Loading',
    'script'      : '',
    'time-step'   : '0.001*ms',
    'elements'    : [
      { 'channel' : 'MOT Detuning',
        'time'    : 'v + 1',
        'value'   : '1.3',
        'enabled' : True},
    ],
    'enabled'     : True,
  },
  { 'group-label' : 'Compressed MOT',
    'script'      : '',
    'time-step'   : 'us',
    'elements'    : [
      { 'channel' : 'MOT Detuning',
        'time'    : '100',
        'value'   : '100m',
        'enabled' : True},
    ],
    'enabled'     : True,
  },
  { 'group-label' : 'Magnetic Capture',
    'script'      : 'capture_dt = 100',
    'time-step'   : 'ms',
    'elements'    : [
      { 'channel' : 'MOT Power',
        'time'    : 'capture_dt',
        'value'   : '10m',
        'enabled' : True},
      { 'channel' : 'U current',
        'time'    : 'capture_dt',
        'value'   : '10m',
        'enabled' : True},
      { 'channel' : 'Z current',
        'time'    : 'capture_dt',
        'value'   : '10m',
        'enabled' : True},
    ],
    'enabled'     : True,
  },
  { 'group-label' : 'Magnetic Release',
    'script'      : '',
    'time-step'   : 'ms',
    'elements'    : [
      { 'channel' : 'Z current',
        'time'    : '10 * v/x',
        'value'   : '10',
        'enabled' : True},
    ],
    'enabled'     : True,
  },
] 

signals = [
  { 'source'  : '10MHz',
    'dest'    : 'PXI0',
    'invert'  : False,
  },
  { 'source'  : 'Ext01',
    'dest'    : 'PXI4',
    'invert'  : False,
  },
  { 'source'  : 'Ext02',
    'dest'    : 'PXI5',
    'invert'  : False,
  },
]
### END TEMPORARY CONFIG ###



