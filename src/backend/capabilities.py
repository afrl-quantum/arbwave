# vim: ts=2:sw=2:tw=80:nowrap
"""
Set of capabilities that each driver may support.
"""

class Capabilities:
  def __init__(self):
    pass

  def get_analog_channels():
    return []

  def get_digital_channels():
    return []

  def get_arbitrary_timing_channels():
    return []

  def get_routeable_backplane_signals():
    return []

