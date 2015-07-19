channels = \
{'Camera Trigger': {'device': 'Digital/vp/Dev0/A/0',
                    'enable': True,
                    'interp_order': 0,
                    'interp_smoothing': 0.0,
                    'offset': None,
                    'order': 0,
                    'scaling': [],
                    'units': None,
                    'value': 'False'},
 'ao0': {'device': 'Analog/ni/Dev1/ao0',
         'enable': True,
         'interp_order': 1,
         'interp_smoothing': 0.0,
         'offset': None,
         'order': 1,
         'scaling': [('0', '0'), ('10', '10')],
         'units': 'V',
         'value': '10*V'},
 'ao1': {'device': 'Analog/ni/Dev1/ao1',
         'enable': True,
         'interp_order': 1,
         'interp_smoothing': 0.0,
         'offset': None,
         'order': 2,
         'scaling': [('0', '0'), ('-10', '10')],
         'units': 'V',
         'value': '5*V'}}

waveforms = \
{'current_waveform': 'Default',
 'waveforms': {'Default': [{'channel': 'Camera Trigger',
                            'duration': '10*ms',
                            'enable': True,
                            'time': 't+10*ms',
                            'value': 'pulse()'},
                           {'channel': 'ao0',
                            'duration': '10*ms',
                            'enable': True,
                            'time': 't+10*ms',
                            'value': '2*V'},
                           {'channel': 'ao0',
                            'duration': '10*ms',
                            'enable': True,
                            'time': 't+10*ms',
                            'value': 'ramp(_from=0*V,to=10*V,duration=10*ms)'}]}}

clocks = \
{'vp/Dev0/A/13': {'divider': {'type': int, 'value': 1}},
 'vp/Dev0/Internal_XO': {'scan_rate': {'type': float, 'value': 20000000.0}}}

hosts = \
{'__default__': 'local', 'local': 'localhost'}

version = \
'0.1.8'

signals = \
{('vp/Dev0/A/13', 'TRIG/1'): {'invert': False}}

runnable_settings = \
{}

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

devices = \
{'ni/Dev1/ao': {'clock': {'type': str, 'value': 'vp/Dev0/A/13'},
                'clock-settings': {'edge': {'type': str, 'value': 'rising'},
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
 'vp/Dev0': {'clock': {'type': str, 'value': 'vp/Dev0/Internal_XO'},
             'in': {'daq_clock_modulo': {'type': int, 'value': 0},
                    'divider': {'type': int, 'value': 0},
                    'stop': {'type': int, 'value': 0},
                    'stop_edge': {'type': int, 'value': 0},
                    'trig_edge': {'type': int, 'value': 0},
                    'trig_source': {'type': int, 'value': 0},
                    'trig_type': {'type': int, 'value': 4}},
             'out': {'daq_clock_modulo': {'type': int, 'value': 0},
                     'divider': {'type': int, 'value': 0},
                     'stop': {'type': int, 'value': 0},
                     'stop_edge': {'type': int, 'value': 0},
                     'trig_edge': {'type': int, 'value': 0},
                     'trig_source': {'type': int, 'value': 0},
                     'trig_type': {'type': int, 'value': 4}}}}

