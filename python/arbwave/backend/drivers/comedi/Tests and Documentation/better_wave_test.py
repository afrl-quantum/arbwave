#This is a test for waveform output in arbwave.

#IMPORTANT: to actually make this work you will have to work around unfinished trigger and clock routing
#try commenting out the two "Sigconfig" calls in the "cmd_config" method in subdevice.py
#and replacing them with trig = None and clk = None








channels = \
{'out': {'device': 'Analog/comedi/Dev0/ao/0',
         'enable': True,
         'interp_order': 1,
         'interp_smoothing': 0.0,
         'offset': None,
         'order': 0,
         'scaling': [('-10', '-10'), ('10', '10')],
         'units': 'V',
         'value': '0*V'}}

waveforms = \
{'current_waveform': 'Default',
 'waveforms': {'Default': [{'channel': 'out',
                            'duration': '10*us',
                            'enable': True,
                            'time': 't',
                            'value': 'ramp(10*V)'}]}}

clocks = \
{'comedi/Dev0/Ctr1': {'delay': {'type': float, 'value': 0.0},
                      'duty-cycle': {'type': float, 'value': 0.5},
                      'idle-state': {'type': str, 'value': 'low'},
                      'rate': {'type': float, 'value': 1.0}}}

hosts = \
{'__default__': 'local', 'local': 'localhost'}

version = \
'0.1.7-88-g41cdf97'

signals = \
{('comedi/Dev0/Ctr1', 'comedi/Dev0/PFI0'): {'invert': False},
 ('comedi/Dev0/PFI0', 'comedi/Dev0/ao/SampleClock'): {'invert': False}}

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
{'comedi/Dev0/ao': {'clock': {'type': str, 'value': 'comedi/Dev0/Ctr1'},
                    'clock-settings': {'edge': {'type': str,
                                                'value': 'rising'},
                                       'mode': {'type': str,
                                                'value': 'continuous'}},
                    'default-voltage-range': {'maximum': {'type': float,
                                                          'value': 10.0},
                                              'minimum': {'type': float,
                                                          'value': -10.0}},
                    'trigger': {'edge': {'type': str, 'value': 'rising'},
                                'enable': {'type': bool, 'value': False},
                                'source': {'type': str,
                                           'value': 'comedi/Dev0/PFI1'}},
                    'use-only-onboard-memory': {'type': bool, 'value': True}}}

