# vim: ts=2:sw=2:tw=80:nowrap
"""
This package is responsible for the logic that converts waveforms descriptions
to more explicit channel-specific full waveforms.
"""

import threading

class Processor:
  def __init__(self, plotter):
    self.plotter = plotter
    self.lock = threading.Lock()

  def update(self, channels, waveforms, signals, script,
             update_plot, update_output, run):
    """
    Using classes should call this function.  This function ensures a first
    come, first served policy on updating plots and hardware output.
    """
    try:
      self.lock.acquire()
      self._update(channels, waveforms, signals, script,
                   update_plot, update_output, run)
    finally:
      self.lock.release()

  def _update(self, channels, waveforms, signals, script,
              update_plot, update_output, run):
    """
    Internal function only.  This is the real meat of update().
    """
    if update_plot:
      print 'updating plot...'
    if update_output:
      if run:
        print 'setup waveform output'
      else:
        print 'setup static output'
