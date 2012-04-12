channels = \
{'Camera Trigger': {'device': 'Digital/fake/viewpoint/port0/line1',
                    'enable': True,
                    'order': 7,
                    'scaling': None,
                    'value': 'On'},
 'MOT Detuning': {'device': 'Analog/fake/ni/dev0/ao0',
                  'enable': True,
                  'order': 0,
                  'scaling': None,
                  'value': '15*MHz'},
 'MOT Power': {'device': 'Analog/fake/ni/dev0/ao1',
               'enable': True,
               'order': 1,
               'scaling': None,
               'value': '100*mW'},
 'Probe Power': {'device': 'Digital/fake/viewpoint/port0/line0',
                 'enable': True,
                 'order': 6,
                 'scaling': None,
                 'value': 'Off'},
 'U Wire': {'device': 'Analog/fake/ni/dev0/ao5',
            'enable': True,
            'order': 5,
            'scaling': None,
            'value': '22*A'},
 'X Bias': {'device': 'Analog/fake/ni/dev0/ao2',
            'enable': True,
            'order': 2,
            'scaling': None,
            'value': '12*G'},
 'Y Bias': {'device': 'Analog/fake/ni/dev0/ao3',
            'enable': True,
            'order': 3,
            'scaling': None,
            'value': '.5*G'},
 'Z Bias': {'device': 'Analog/fake/ni/dev0/ao4',
            'enable': True,
            'order': 4,
            'scaling': None,
            'value': '.4*G'}}

waveforms = \
[{'asynchronous': False,
  'duration': '500*ms',
  'elements': [{'channel': 'MOT Detuning',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '5*V'},
               {'channel': 'MOT Power',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '10*V'},
               {'channel': 'X Bias',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '2*V'},
               {'channel': 'Y Bias',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '.2*V'},
               {'channel': 'Z Bias',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '.19*V'},
               {'channel': 'U Wire',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '8*V'}],
  'enable': True,
  'group-label': 'MOT Loading',
  'script': '',
  'time': 't'},
 {'asynchronous': False,
  'duration': '30*ms,ms',
  'elements': [{'channel': 'MOT Detuning',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': 'ramp(10*V,2)'},
               {'channel': 'MOT Power',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': 'ramp(0*V,.5)'},
               {'channel': 'U Wire',
                'duration': 'dt-ms,ddt',
                'enable': True,
                'time': 't',
                'value': 'ramp(10*V,1)'},
               {'channel': 'U Wire',
                'duration': 'ms',
                'enable': True,
                'time': 't',
                'value': '0*V'}],
  'enable': True,
  'group-label': 'CMOT',
  'script': '',
  'time': 't'},
 {'asynchronous': True,
  'duration': '100*us',
  'elements': [{'channel': 'Probe Power',
                'duration': 'dt/2',
                'enable': True,
                'time': 't',
                'value': 'On'},
               {'channel': 'Camera Trigger',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': 'On'},
               {'channel': 'Probe Power',
                'duration': 'dt/2',
                'enable': True,
                'time': 't',
                'value': 'Off'}],
  'enable': True,
  'group-label': 'Imaging',
  'script': '',
  'time': 't'},
 {'asynchronous': False,
  'duration': '10*ms',
  'elements': [{'channel': 'MOT Detuning',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '5*V'},
               {'channel': 'MOT Power',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '10*V'},
               {'channel': 'U Wire',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '0*V'},
               {'channel': 'Probe Power',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': 'Off'},
               {'channel': 'Camera Trigger',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': 'Off'}],
  'enable': True,
  'group-label': 'Final Values',
  'script': '',
  'time': 't+100*ms'}]

global_script = \
"""# This script sets global variables and/or functions.
# All other scripts and processing will be done in this context.
from physical.unit import *
from physical.constant import *
from physical import unit
Off = False
On = True

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
