# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Some details of the DDS front end implementation done here in order to allow
these details to be used by the simulation.
"""

from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog
import copy
import itertools

class Details(object):
  def set_output(self, values):
    """
    This function takes channel outputs as a dictionary where the values are in
    voltage:
      values = {'<channel#>' : <value in volts>, ...}

    such as
      values = {'0' : 0.0, '1' : 1.1}
    for
      channel 0 : 0 V
      channel 1 : 1.1 V
    """
    # ensure we convert to DAC scale and put back into dict
    V = {int(ch): self.volts_to_DAC(int(ch), v) for ch, v in values.items()}
    self.base_set_output(V)


  def set_waveforms(self, waveforms, transitions):
    """
    Set the output waveforms for the AFRL/BeagleBone Black device.

    :param waveforms:
      a dict('channel': {<wfe-path>: (<encoding>, [(t1, val1), (t2, val2)])})
                      (see gui/plotter/digital.py for format)
                      where wfe-path means waveform element path, referring to
                      the unique identifier of the specific waveform element a
                      particular set of values refers to.
    :param transitions: Sorted list of transitions for the clock that is
                      providing update pulses to this device.  This may include
                      transitions that this device needs to pad its output for
                      (for example, if another channel is using this same
                      clock).

    This function has to convert:
    clock_transitions = [
      0,
      33400,
      40067,
      45000,
      50067,
    ]
    waveforms={
      '1': {
        (-1,): ('step', [(0, 2898)]),
        (2, 5): ('step', [(33400, 3098)]),
      },
      '0': {
        (-1,): ('step', [(0, 50000.0)]),
        (2, 2): ('step', [(33400, 33299)]),
        (2, 3): ('step', [(40067, 30000)]),
        (2, 4): ('step', [(50067, 40000)]),
      },
    }
    
    to
    
    [
      # <channel0>,    <channel1>            t
      50000,           2898, #  0
      33299,           3098, #  33400
      30000,           3098, #  40067
      30000,           3098, #  45000 (hold-over/pad transition)
      40000,           3098, #  50067
    ]
    
    then to (using scalar conversion to 16-bit integer output)
    """

    # array of all scan info for all transitions
    scans = dict.fromkeys( transitions )
    nones = [None] * len(waveforms)
    indx_to_channel = list()
    channel_to_indx = dict()
    channel_bits = 0b0

    # loop through each transition and accumulate a list of scans for each
    # channel for each transition.
    waveforms = sorted(waveforms.items(), key=lambda ch_data : int(ch_data[0]))
    for ch_indx, (ch, grouped_ch_transitions) in enumerate(waveforms):
      ch = int(ch)
      assert 0 <= ch < 16, 'bbb.analog.set_waveform: unknown channel: ' +str(ch)

      indx_to_channel.append(ch)
      channel_to_indx[ch] = ch_indx
      channel_bits |= (1 << ch)
      for wf_path, (encoding, group_trans) in grouped_ch_transitions.items():
        assert encoding == 'step', \
          'invalid non-step transition encoding for bbb.analog: '+encoding

        for timestamp, value in group_trans:
          if scans[timestamp] is None:
            # first time this timestamp has scan data
            scans[timestamp] = copy.copy( nones )
          # be sure to convert to DAC digital value from volts
          scans[timestamp][ch_indx] = self.volts_to_DAC(ch, value)

    # fix the beginning of the waveform
    S0 = scans[ transitions[0] ]
    if S0 is None:
      # must be sharing a clock with another card.  init all channels to zero
      warn('bbb.analog: missing start values for all channel--using 0*V')
      scans[ transitions[0] ] = [
        self.volts_to_DAC(ch, 0) for ch in indx_to_channel]
    else:
      for i, v in enumerate(S0):
        if v is None:
          ch = indx_to_channel[i]
          warn('bbb.analog: missing start value for channel %s--using 0*V', ch)
          S0[i] = self.volts_to_DAC(ch, 0)

    last = scans[ transitions[0] ]

    # All remaining none values mean that the prior value for the particular
    # channels(s) should be kept for that scan.
    for t in transitions:
      t_array = scans[t]
      if t_array is None:
        # must be sharing a clock with another card.  keep last values
        scans[t] = last
      else:
        for i in range( len(waveforms) ):
          if t_array[i] is None:
            t_array[i] = last[i]
        last = t_array

    # now, we finally build the actual data to send to the hardware
    flat_waveform = list(
      itertools.chain.from_iterable([ scans[t]  for t in transitions ]))

    # 3b.  send data to hardware
    debug( 'bbb.analog: waveform for channel bits "%s"', bin(channel_bits) )
    if rootlog.getEffectiveLevel() <= (DEBUG-1):
      log(DEBUG-1, 'bbb.analog.waveform[:] = %s', repr(flat_waveform))
      log(DEBUG-1, 'bbb.analog.waveform.times = %s', repr(transitions))

    # just some dummy checks
    n_channels = sum([((channel_bits >> i) & 0b1) for i in range(16)])
    wlen = len(flat_waveform) / n_channels
    if wlen != int(wlen):
      raise RuntimeError(
        'Waveform is not sized correctly for the number participating channels')

    self.load_waveform(int(wlen), channel_bits, flat_waveform)
