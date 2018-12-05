hosts = \
{'__default__': 'local', 'local': 'localhost'}

devices = \
{'ni/Dev1/ao': {'clock': {'type': str, 'value': 'ni/Dev1/ao/SampleClock'},
                'clock-settings': {'Timebase': {'clock': {'type': str,
                                                          'value': ''}},
                                   'edge': {'type': str, 'value': 'rising'},
                                   'mode': {'type': str,
                                            'value': 'continuous'}},
                'default-voltage-range': {'maximum': {'type': float,
                                                      'value': 10.0},
                                          'minimum': {'type': float,
                                                      'value': -10.0}},
                'trigger': {'edge': {'type': str, 'value': 'rising'},
                            'enable': {'type': bool, 'value': False},
                            'source': {'type': str, 'value': ''}},
                'use-only-onboard-memory': {'type': bool, 'value': True}},
 'ni/Dev1/do': {'clock': {'type': str, 'value': 'ni/Dev1/ao/SampleClock'},
                'clock-settings': {'Timebase': {'clock': {'type': str,
                                                          'value': ''}},
                                   'edge': {'type': str, 'value': 'rising'},
                                   'mode': {'type': str,
                                            'value': 'continuous'}},
                'use-only-onboard-memory': {'type': bool, 'value': True}}}

clocks = \
{'ni/Dev1/ao/SampleClock': {'rate': {'type': float, 'value': 2000.0}}}

global_script = \
"""# This script sets global variables and/or functions.
# All other scripts and processing will be done in this context.
from physical.unit import *
from physical.constant import *
from physical import unit
import Arbwave

class SimpleRun(Arbwave.Runnable):
	def run(self):
		Arbwave.update()
		# if possible, the run function should return a value indicative of the
		# performance of the particular run.  Below is just a "random" example.
		import random
		return random.randint(0,100)

Arbwave.add_runnable( 'Simple', SimpleRun() )
"""

channels = \
{'ao0': {'device': 'analog/ni/Dev1/ao0',
         'enable': True,
         'interp_order': 1,
         'interp_smoothing': 0.0,
         'offset': None,
         'order': 0,
         'plot_scale_factor': 1.0,
         'plot_scale_offset': 0.0,
         'scaling': [('-10', '-10'), ('10', '10')],
         'units': 'V',
         'value': '1*V'},
 'do0': {'device': 'digital/ni/Dev1/port0/line0',
         'enable': True,
         'interp_order': 0,
         'interp_smoothing': 0.0,
         'offset': None,
         'order': 1,
         'plot_scale_factor': 1.0,
         'plot_scale_offset': 0.0,
         'scaling': None,
         'units': None,
         'value': 'False'}}

waveforms = \
{'current_waveform': 'Default',
 'waveforms': {'Default': [{'asynchronous': False,
                            'duration': '100*ms',
                            'elements': [{'channel': 'ao0',
                                          'duration': 'dt/2',
                                          'enable': True,
                                          'time': 't',
                                          'value': '1*V'},
                                         {'channel': 'ao0',
                                          'duration': 'dt/2',
                                          'enable': True,
                                          'time': 't',
                                          'value': 'ramp(5*V,steps=99)'},
                                         {'channel': 'do0',
                                          'duration': '',
                                          'enable': True,
                                          'time': 't',
                                          'value': 'pulses(10)'}],
                            'enable': True,
                            'group-label': 'Group 0',
                            'script': None,
                            'time': 't'},
                           {'asynchronous': False,
                            'duration': '100*ms',
                            'elements': [{'channel': 'ao0',
                                          'duration': 'dt/2',
                                          'enable': True,
                                          'time': 't',
                                          'value': '1*V'},
                                         {'channel': 'ao0',
                                          'duration': 'dt/2',
                                          'enable': True,
                                          'time': 't',
                                          'value': 'sinpulse(5*V, 50*Hz)'},
                                         {'channel': 'do0',
                                          'duration': '',
                                          'enable': True,
                                          'time': 't',
                                          'value': 'pulses(10)'}],
                            'enable': True,
                            'group-label': 'Group 1',
                            'script': None,
                            'time': 't'}]}}

signals = \
{}

version = \
'1.1.0'

runnable_settings = \
{'Simple:  Loop': {'parameters': [{'enable': True,
                                   'isglobal': False,
                                   'iterable': 'range(0,10,2)',
                                   'name': 'i'}]}}

