channels = \
{'Camera Trigger': {'device': 'Digital/fake/viewpoint/port0/line1',
                    'enable': True,
                    'order': 8,
                    'scaling': [],
                    'units': '',
                    'interp_order' : 1,
                    'interp_smoothing' : 0.0,
                    'value': 'On'},
 'MOT Detuning': {'device': 'Analog/fake/ni/dev0/ao0',
                  'enable': True,
                  'order': 0,
                  'scaling': [('0', '-10'),
                              ('1.22', '0'),
                              ('2', '3'),
                              ('10', '30')],
                  'units': 'MHz',
                  'interp_order' : 1,
                  'interp_smoothing' : 0.0,
                  'value': '15*MHz'},
 'MOT Power': {'device': 'Analog/fake/ni/dev0/ao1',
               'enable': True,
               'order': 1,
               'scaling': [('0', '0'), ('1', '20')],
               'units': 'mW',
               'interp_order' : 1,
               'interp_smoothing' : 0.0,
               'value': '100*mW'},
 'MOT Shutter': {'device': 'Digital/fake/viewpoint/port0/line2',
                 'enable': True,
                 'order': 2,
                 'scaling': [],
                 'units': '',
                 'interp_order' : 1,
                 'interp_smoothing' : 0.0,
                 'value': 'On'},
 'Probe Power': {'device': 'Digital/fake/viewpoint/port0/line0',
                 'enable': True,
                 'order': 7,
                 'scaling': [],
                 'units': '',
                 'interp_order' : 1,
                 'interp_smoothing' : 0.0,
                 'value': 'Off'},
 'U Wire': {'device': 'Analog/fake/ni/dev0/ao5',
            'enable': True,
            'order': 6,
            'scaling': [('0', '0'), ('1', '20')],
            'units': 'A',
            'interp_order' : 1,
            'interp_smoothing' : 0.0,
            'value': '22*A'},
 'X Bias': {'device': 'Analog/fake/ni/dev0/ao2',
            'enable': True,
            'order': 3,
            'scaling': [('-1', '-.2'), ('0', '0'), ('1', '.2')],
            'units': 'G',
            'interp_order' : 1,
            'interp_smoothing' : 0.0,
            'value': '12*G'},
 'Y Bias': {'device': 'Analog/fake/ni/dev0/ao3',
            'enable': True,
            'order': 4,
            'scaling': [('-1', '.2'), ('0.05', '0'), ('1', '-.3')],
            'units': 'G',
            'interp_order' : 1,
            'interp_smoothing' : 0.0,
            'value': '.5*G'},
 'Z Bias': {'device': 'Analog/fake/ni/dev0/ao4',
            'enable': True,
            'order': 5,
            'scaling': [('-1', '.4'), ('-.05', '0'), ('1', '-.3')],
            'units': 'G',
            'interp_order' : 1,
            'interp_smoothing' : 0.0,
            'value': '.4*G'}}

waveforms = \
[{'asynchronous': False,
  'duration': '500*ms',
  'elements': [{'channel': 'MOT Shutter',
                'duration': '',
                'enable': True,
                'time': 't-100*ms',
                'value': 'On'},
               {'channel': 'MOT Detuning',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '5*MHz'},
               {'channel': 'MOT Power',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '10*mW'},
               {'channel': 'X Bias',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '2*G'},
               {'channel': 'Y Bias',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '.2*G'},
               {'channel': 'Z Bias',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '.19*G'},
               {'channel': 'U Wire',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '8*A'}],
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
                'value': 'ramp(10*MHz,2)'},
               {'channel': 'MOT Power',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': 'ramp(0*mW,.5)'},
               {'channel': 'MOT Shutter',
                'duration': '',
                'enable': True,
                'time': 't+dt',
                'value': 'Off'},
               {'channel': 'U Wire',
                'duration': 'dt-ms,ddt',
                'enable': True,
                'time': 't',
                'value': 'ramp(10*A,1)'},
               {'channel': 'U Wire',
                'duration': 'ms',
                'enable': True,
                'time': 't',
                'value': '0*A'}],
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
                'duration': 'dt/2',
                'enable': True,
                'time': 't',
                'value': 'On'},
               {'channel': 'Probe Power',
                'duration': 'dt/2',
                'enable': True,
                'time': 't',
                'value': 'Off'},
               {'channel': 'Camera Trigger',
                'duration': 'dt/2',
                'enable': True,
                'time': 't',
                'value': 'Off'}],
  'enable': True,
  'group-label': 'Imaging',
  'script': '',
  'time': 't'},
 {'asynchronous': False,
  'duration': '3000*ms',
  'elements': [{'channel': 'MOT Detuning',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '5*MHz'},
               {'channel': 'MOT Power',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '10*mW'},
               {'channel': 'U Wire',
                'duration': '',
                'enable': True,
                'time': 't',
                'value': '0*A'}],
  'enable': True,
  'group-label': 'MOT Nap',
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

shutter = dict()
shutter['MOT/On'] = 4*ms

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

