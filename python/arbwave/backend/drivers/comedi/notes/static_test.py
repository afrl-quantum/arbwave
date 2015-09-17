#!/usr/bin/env python

#very old test to generate static output while bypassing the Arbwave gui
#should no longer be needed as Arbwave can provide all needed inputs

import arbwave.backend.drivers.comedi as COM



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
                  {'type': str, 'value': ''},
                   'default-voltage-range':
                        {'minimum': {'type': float, 'value': 0.0},
                         'maximum': {'type': float, 'value': 5.0}}}}






channels = {'comedi/Dev0/ao0': {'max': 10, 'order': 0, 'min': -10},



#without routing, paths seem to have no effect
paths = {'comedi/Dev0/PFI0': ({'comedi/Dev0/PFI0': None},
                                 {'comedi/Dev0/PFI0': 0})}

analog =

driver.set_device_config(configA, channels, paths)

driver.set_static(analog,digital)


#print driver.get_analog_channels()

#print 'config template: ', driver.get_devices()[0].get_config_template()

#found conflict with new method of including subdevice number in key in driver.subdevices. 'analog' looks for subdevices witht the earlier convention, so the number will cause a key error. for now, will ignore to complete test.


#Why does dio subdevice claim to have 32 chans but only has ranges fo the first 4?

#it's possible that for digital output the device should not be comedi0 but instead comedi0_subd2
#it's also possible that where a channel is configured for output matters

#changed to bitfield, no commands
# dio command still configures in case of need
## DIO output working, but while loop required to prevent underwrite
## DIO output must have external clock and cannot use CR_EDGE in the scan begin arg!


#this all should fail if analog data is given to a digital subdevice and in the converse case. I think this is a good feature, but it plausibly could cause problems in the future

