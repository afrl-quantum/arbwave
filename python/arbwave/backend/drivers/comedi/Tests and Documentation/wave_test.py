#!/usr/bin/env python

import arbwave.backend.drivers.comedi as COM
import physical
from physical import unit

#outdated test of waveforms

driver = COM.Driver()

configA = {'comedi/Dev0/ao1': # used subdevice, might be wrong
              {'use-only-onboard-memory':
                  {'type': bool, 'value': True},
              'clock-settings':
                  {'edge': {'type': str, 'value': 'rising'},
                   'mode':  {'type': str, 'value': 'continuous'}},
              'trigger':
                  {'source': {'type': str, 'value': ''},
                   'enable': {'type': bool, 'value': False},
                   'edge': {'type': str, 'value': 'rising'}},
              'clock':
                  {'type': str, 'value': 'comedi/Dev0/to/0'},
                   'default-voltage-range':
                        {'minimum': {'type': float, 'value': -10.0},
                         'maximum': {'type': float, 'value': 10.0}}}}






channels = {'comedi/Dev0/ao0': {'max': 10, 'order': 0, 'min': -10}}



#without routing, paths seem to have no effect
paths = {'comedi/Dev0/to/0': ({'comedi/Dev0/ao/SampleClockTimebase': None}, {'comedi/Dev0/ao/SampleClockTimebase': 0})
        }

analog = {'comedi/Dev0/ao0': {(0, 0):[(750000, float(7)),(250000,float(3)),(500000,float(5))], (-1,):[(0, float(-2))]}}

transitions = {'comedi/Dev0/to/0': {'dt': (20)*unit.s , 'transitions': set([0,750000, 250000, 500000])}}

t_max = 0.01

end_clocks = set(['comedi/Dev0/to/0'])

digital = dict()


driver.set_device_config(configA, channels, paths)


driver.set_waveforms(analog, digital, transitions, t_max, end_clocks, True)



