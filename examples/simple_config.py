channels = \
{'MOT Detuning': {'device': '/dev0/ao0',
                  'enable': True,
                  'scaling': 'min(10,max(-10,{value}/1.5))',
                  'value': '10*300'},
 'MOT Power': {'device': '/dev0/ao1',
               'enable': True,
               'scaling': 'min(10,max(-10,{value}))',
               'value': '10*300'},
 'U Current': {'device': '/dev0/ao2',
               'enable': True,
               'scaling': 'min(10,max(-10,{value}))',
               'value': '10*300'},
 'Z Current': {'device': '/dev0/ao3',
               'enable': True,
               'scaling': 'min(10,max(-10,{value}))',
               'value': '10*300'}}

waveforms = \
[{'elements': [{'channel': 'MOT Detuning',
                'enable': True,
                'time': 'v + 1',
                'value': '1.3'}],
  'enable': True,
  'group-label': 'MOT Loading',
  'script': '',
  'time-step': '0.001*ms'},
 {'elements': [{'channel': 'MOT Detuning',
                'enable': True,
                'time': '100',
                'value': '100m'}],
  'enable': True,
  'group-label': 'Compressed MOT',
  'script': '',
  'time-step': 'us'},
 {'elements': [{'channel': 'MOT Power',
                'enable': True,
                'time': 'capture_dt',
                'value': '10m'},
               {'channel': 'U current',
                'enable': True,
                'time': 'capture_dt',
                'value': '10m'},
               {'channel': 'Z current',
                'enable': True,
                'time': 'capture_dt',
                'value': '10m'}],
  'enable': True,
  'group-label': 'Magnetic Capture',
  'script': 'capture_dt = 100',
  'time-step': 'ms'},
 {'elements': [{'channel': 'Z current',
                'enable': True,
                'time': '10 * v/x',
                'value': '10'}],
  'enable': True,
  'group-label': 'Magnetic Release',
  'script': '',
  'time-step': 'ms'}]

global_script = \
"""# This script sets global variables and/or functions.
# All other scripts and processing will be done in this context.
from math import pi

cm = 0.01
some_variable = pi * ( 10*cm )**2.0

def onstart():
	'''Called when 'play' button is clicked'''
	pass

def onstop():
	'''Called when 'stop' button is clicked.'''
	pass

import arbwave
def loop_control(*args, **kwargs):
	for i in [1,2,3]:
		for j in [1,2,3]:
			arbwave.update()

arbwave.connect( 'start', onstart )
arbwave.connect( 'stop', onstop )
#arbwave.set_loop_control( loop_control )
"""

signals = \
[{'dest': 'PXI0', 'invert': False, 'source': '10MHz'},
 {'dest': 'PXI4', 'invert': False, 'source': 'Ext01'},
 {'dest': 'PXI5', 'invert': False, 'source': 'Ext02'}]

