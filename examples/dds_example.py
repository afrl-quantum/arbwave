hosts = \
{'__default__': 'local', 'local': 'localhost'}

devices = \
{'bbb/bbb0/dds': {'clock': {'type': str, 'value': 'bbb/bbb0/timing/0'},
                  'pll_chargepump': {'type': str, 'value': '75uA'},
                  'refclk': {'frequency': {'type': float, 'value': 10000000.0},
                             'source': {'type': str, 'value': 'tcxo'}},
                  'sysclk': {'type': float, 'value': 500000000.0}},
 'bbb/bbb0/timing': {'clock': {'type': str,
                               'value': 'bbb/bbb0/timing/InternalClock'},
                     'start_delay': {'type': float,
                                     'value': 1.5000000000000002e-08},
                     'trigger': {'enable': {'type': bool, 'value': False},
                                 'level': {'type': str, 'value': 'low'},
                                 'pull': {'type': str, 'value': 'down'},
                                 'retrigger': {'type': bool, 'value': False}}}}

clocks = \
{'bbb/bbb0/timing/0': {'divider': {'type': int, 'value': 2}},
 'bbb/bbb0/timing/InternalClock': {}}

global_script = \
"""# This is a simple example of using the AFRL DDS Cape to generate frequencies,
# such as
# 1) an arbitrary low frequency (on channel "dds0")
# 2) a laser detuning centered around some zero-offset frequency (on channel
#    "detuning")
#
# This example also demonstrates how the plot can be offset and rescaled in
# order to show something both meaningful and also on something near the same
# scale as the other channels.

# This script sets global variables and/or functions.
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
{'dds0': {'device': 'dds/bbb/bbb0/dds/0',
          'enable': True,
          'interp_order': 1,
          'interp_smoothing': 0.0,
          'offset': None,
          'order': 0,
          'plot_scale_factor': 1.0,
          'plot_scale_offset': 0.0,
          'scaling': [],
          'units': 'Hz',
          'value': '10*Hz'},
 'detuning': {'device': 'dds/bbb/bbb0/dds/1',
              'enable': True,
              'interp_order': 1,
              'interp_smoothing': 0.0,
              'offset': None,
              'order': 1,
              'plot_scale_factor': 6.4e-05,
              'plot_scale_offset': 50000000.0,
              'scaling': [('34.375e6', '-1000'), ('65.625e6', '1000')],
              'units': 'MHz',
              'value': '0*MHz'},
 'do0': {'device': 'digital/bbb/bbb0/timing/1',
         'enable': True,
         'interp_order': 1,
         'interp_smoothing': 0.0,
         'offset': None,
         'order': 2,
         'plot_scale_factor': 1.0,
         'plot_scale_offset': 0.0,
         'scaling': None,
         'units': None,
         'value': 'False'}}

waveforms = \
{'current_waveform': 'Default',
 'waveforms': {'Default': [{'asynchronous': False,
                            'duration': '100*ms',
                            'elements': [{'channel': 'detuning',
                                          'duration': 'dt/2',
                                          'enable': True,
                                          'time': 't',
                                          'value': 'U0 + (-10*MHz - U0)*x'},
                                         {'channel': 'detuning',
                                          'duration': 'dt/2',
                                          'enable': True,
                                          'time': 't',
                                          'value': '50*MHz'},
                                         {'channel': 'dds0',
                                          'duration': '',
                                          'enable': True,
                                          'time': 't',
                                          'value': 'U0 + (100*Hz - U0)*x**2'},
                                         {'channel': 'do0',
                                          'duration': 'dt/2',
                                          'enable': True,
                                          'time': 't',
                                          'value': 'pulse()'}],
                            'enable': True,
                            'group-label': 'G0',
                            'script': None,
                            'time': 't'}]}}

signals = \
{}

version = \
'1.2.0-22-g35f8827'

runnable_settings = \
{}

