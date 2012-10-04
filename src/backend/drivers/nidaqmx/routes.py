# vim: ts=2:sw=2:tw=80:nowrap
"""
  The set of routes that are possible depending on the particular hardware.
"""

# map (src, destination) -> (native-src, native-destination)
signal_route_map = dict()

available = {
  'PCI-6723' : {
    ('External/', None) : {
      'PFI{0..9}',
    },
    'PFI{0..9}' : {
      'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}',
      'Ctr{0..1}{Gate,Source}',
      ('External/', None),
    },
    ('TRIG/{0..6}','RTSI{0..6}') : {
      'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}',
      'Ctr{0..1}{Out,Gate,Source}',
    },
    ('TRIG/7','RTSI7') : {
      'ao/SampleClockTimebase',
      'Ctr{0..1}Source',
    },
    'Ctr0Out' : {
      ('TRIG/{0..6}','RTSI{0..6}'),
    },
    'Ctr0Gate' : {
      'PFI9',
      ('TRIG/{0..6}','RTSI{0..6}'),
    },
    'Ctr0Source' : {
      'PFI8',
      ('TRIG/{0..6}','RTSI{0..6}'),
    },
    'Ctr0InternalOutput' : {
      ('TRIG/{0..6}','RTSI{0..6}'),
      'Ctr0Out',
      'Ctr1Gate',
    },
    'Ctr1Gate' : {
      'PFI4',
    },
    'Ctr1Source' : {
      'PFI3',
    },
    'Ctr1InternalOutput' : {
      'ao/SampleClock',
      'Ctr1Out',
      'Ctr0Gate',
    },
  },


  'PXI-6733' : {
    ('External/', None) : {
      'PFI{0..9}',
    },
    'PFI{0..9}' : {
      'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}',
      'Ctr{0..1}{Gate,Source}',
      ('External/', None),
    },
    ('TRIG/{0..6}','{PXI_Trig{0..5},PXI_Star}') : {
      'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}',
      'Ctr{0..1}{Out,Gate,Source}',
    },
    ('TRIG/7','PXI_Trig7') : {
      'ao/SampleClockTimebase',
      'Ctr{0..1}Source',
    },
    'Ctr0Out' : {
      ('TRIG/{0..6}','{PXI_Trig{0..5},PXI_Star}'),
    },
    'Ctr0Gate' : {
      'PFI9',
      ('TRIG/{0..6}','{PXI_Trig{0..5},PXI_Star}'),
    },
    'Ctr0Source' : {
      'PFI8',
      ('TRIG/{0..6}','{PXI_Trig{0..5},PXI_Star}'),
    },
    'Ctr0InternalOutput' : {
      ('TRIG/{0..6}','{PXI_Trig{0..5},PXI_Star}'),
      'Ctr0Out',
      'Ctr1Gate',
    },
    'Ctr1Gate' : {
      'PFI4',
    },
    'Ctr1Source' : {
      'PFI3',
    },
    'Ctr1InternalOutput' : {
      'ao/SampleClock',
      'Ctr1Out',
      'Ctr0Gate',
    },
  },
}
