channels = \
{'MOT Detuning': {'device': '/dev0/ao0',
                  'enable': True,
                  'scaling': 'min(10,max(-10,{value}/1.5))',
                  'value': '12*MHz'},
 'MOT Power': {'device': '/dev0/ao1',
               'enable': True,
               'scaling': 'min(10,max(-10,{value}))',
               'value': '20*mW'},
 'U Current': {'device': '/dev0/ao2',
               'enable': True,
               'scaling': 'min(10,max(-10,{value}))',
               'value': '20*A'},
 'Z Current': {'device': '/dev0/ao3',
               'enable': True,
               'scaling': 'min(10,max(-10,{value}))',
               'value': '25*A'}}

waveforms = \
[{'elements': [{'channel': 'MOT Detuning',
                'enable': True,
                'time': 't',
                'duration': '',
                'value': '15*MHz'},
               {'channel': 'MOT Power',
                'enable': True,
                'time': 't',
                'duration': '',
                'value': '20*mW'}],
  'enable': True,
  'asynchronous' : False,
  'group-label': 'MOT Loading',
  'time'  : 't',
  'duration' : '10*ms',
  'script': ''},
 {'elements': [{'channel': 'MOT Detuning',
                'enable': True,
                'time': 't',
                'duration' : '5*ms',
                'value': 'ramp(to=40*MHz, exponent=.5)'},
               {'channel': 'MOT Power',
                'enable': True,
                'time': 't',
                'duration': '',
                'value': '20*mW'}],
  'enable': True,
  'asynchronous' : False,
  'group-label': 'Compressed MOT',
  'time'  : 't',
  'duration' : '10*ms',
  'script': ''},
 {'elements': [{'channel': 'MOT Power',
                'enable': True,
                'time': 't',
                'duration': '30*ms,.1*ms',
                'value': 'ramp(0*mW,.5)'},
               {'channel': 'U current',
                'enable': True,
                'time': 't',
                'duration':'',
                'value': 'ramp(0*A, .5)'},
               {'channel': 'Z current',
                'enable': True,
                'time': 't',
                'duration':'dt,.1*ms',
                'value': 'ramp(50*A, 2)'}],
  'enable': True,
  'asynchronous' : False,
  'group-label': 'Magnetic Capture',
  'time'  : 't',
  'duration' : '50*ms',
  'script': 'capture_dt = 100'},
 {'elements': [{'channel': 'MOT Detuning',
                'enable': True,
                'time': 't',
                'duration':'',
                'value': '15*MHz'},
               {'channel': 'MOT Power',
                'enable': True,
                'time': 't+5ms',
                'duration':'',
                'value': '20*mW'},
               {'channel': 'Z current',
                'enable': True,
                'time': 't',
                'duration':'',
                'value': '0'}],
  'enable': True,
  'asynchronous' : False,
  'time'  : 't',
  'duration':'10*ms',
  'group-label': 'Magnetic Release',
  'script': ''}]

global_script = \
"""# This script sets global variables and/or functions.
# All other scripts and processing will be done in this context.
from physical.unit import *
from physical.constant import *
from physical import unit

print 'updating global environment...'
some_variable = pi * ( 10*cm )**2.0
other_variable = 1

def onstart():
	'''Called when 'play' button is clicked'''
	print 'starting!!!!'

def onstop():
	'''Called when 'stop' button is clicked.'''
	print 'stopping!!!!'

import arbwave, time
def loop_control(*args, **kwargs):
	global some_variable, other_variable
	for i in [1,2,3]:
		some_variable += mm**2.0
		for j in [1,2,3]:
			other_variable +=2
			arbwave.update()
			time.sleep(2)

arbwave.connect( 'start', onstart )
arbwave.connect( 'stop', onstop )
arbwave.set_loop_control( loop_control )
"""

signals = \
[{'dest': 'PXI0', 'invert': False, 'source': '10MHz'},
 {'dest': 'PXI4', 'invert': False, 'source': 'Ext01'},
 {'dest': 'PXI5', 'invert': False, 'source': 'Ext02'}]

