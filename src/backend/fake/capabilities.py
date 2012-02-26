# vim: ts=2:sw=2:tw=80:nowrap
"""
Set of capabilities that each driver may support.
"""

from ..capabilities import Capabilities as Base

class Capabilities(Base):
  def __init__(self):
    pass

  def get_analog_channels():
    return [
      '/dev0/ao0',
      '/dev0/ao1',
      '/dev0/ao2',
      '/dev0/ao3',
    ]

  def get_digital_channels():
    return [
      '/dev1/port0/line0',
      '/dev1/port0/line1',
      '/dev1/port0/line2',
      '/dev1/port0/line3',
      '/dev1/port0/line4',
      '/dev1/port0/line5',
      '/dev1/port0/line6',
      '/dev1/port0/line7',
      '/dev1/port1/line0',
      '/dev1/port1/line1',
      '/dev1/port1/line2',
      '/dev1/port1/line3',
      '/dev1/port1/line4',
      '/dev1/port1/line5',
      '/dev1/port1/line6',
      '/dev1/port1/line7',
      '/viewpoint/port0/line0',
      '/viewpoint/port0/line1',
      '/viewpoint/port0/line2',
      '/viewpoint/port0/line3',
      '/viewpoint/port0/line4',
      '/viewpoint/port0/line5',
      '/viewpoint/port0/line6',
      '/viewpoint/port0/line7',
    ]

  def get_arbitrary_timing_channels():
    return [
      '/viewpoint/port0/line0',
      '/viewpoint/port0/line1',
      '/viewpoint/port0/line2',
      '/viewpoint/port0/line3',
      '/viewpoint/port0/line4',
      '/viewpoint/port0/line5',
      '/viewpoint/port0/line6',
      '/viewpoint/port0/line7',
    ]

  def get_routeable_backplane_signals():
    return [
      '/PXI/0',
      '/PXI/1',
      '/PXI/2',
      '/PXI/3',
      '/PXI/4',
      '10MHzClock',
      '20MHzClock',
      '/PAF/0',
      '/PAF/1',
      '/PAF/2',
      '/PAF/3',
      '/PAF/4',
      '/PAF/5',
      '/PAF/6',
      '/PAF/7',
    ]

