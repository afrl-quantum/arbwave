# vim: ts=2:sw=2:tw=80:nowrap
"""
  The set of routes that are possible depending on the particular hardware.
"""

available = {
  'PCI-6723' : {
    'PFI{0..9}' : {
      'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}',
      'ctr{0..1}{Gate,Source}',
      ('External/', None),
    },
    ('TRIG/{0..6}','RTSI{0..6}') : {
      'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}',
      'ctr{0..1}{Out,Gate,Source}',
    },
    ('TRIG/7','RTSI7') : {
      'ao/SampleClockTimebase',
      'ctr{0..1}Source',
    },
    'ctr0Out' : {
      ('TRIG/{0..6}','RTSI{0..6}'),
    },
    'ctr0Gate' : {
      'PFI9',
      ('TRIG/{0..6}','RTSI{0..6}'),
    },
    'ctr0Source' : {
      'PFI8',
      ('TRIG/{0..6}','RTSI{0..6}'),
    },
    'ctr0InternalOutput' : {
      ('TRIG/{0..6}','RTSI{0..6}'),
      'ctr0Out',
      'ctr1Gate',
    },
    'ctr1Gate' : {
      'PFI4',
    },
    'ctr1Source' : {
      'PFI3',
    },
    'ctr1InternalOutput' : {
      'ao/SampleClock',
      'ctr1Out',
      'ctr0Gate',
    },
  },
}
