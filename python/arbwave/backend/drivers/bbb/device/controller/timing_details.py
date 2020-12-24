# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Some details of the Timing front end implementation done here in order to allow
these details to be used by the simulation.
"""

from physical import unit

class Details(object):
  def set_waveforms(self, waveforms, clock_transitions, t_max):
    """
    Set the output waveforms for the AFRL/BeagleBone Black device.

    :param waveforms:
      a dict('channel': {<wfe-path>: (<encoding>, [(t1, val1), (t2, val2)])})
                      (see gui/plotter/digital.py for format)
                      where wfe-path means waveform element path, referring to
                      the unique identifier of the specific waveform element a
                      particular set of values refers to.
    :param clock_transitions: a dict('channel': { 'dt': dt,
                              'transitions': iterable})
                              (see processor/engine/compute.py for format)
    :param t_max: the maximum duration of any channel in units of time.
    """
    if set(waveforms.keys()).intersection(clock_transitions.keys()):
      raise RuntimeError('bbb::timing channels cannot be used as clocks and ' \
                         'digital output simultaneously')

    transition_map = self._compile_transition_map(waveforms, clock_transitions, t_max)
    self.set_waveform_size(len(transition_map) - 1) # one is a dummy at the end
    self._load_transitions(transition_map)


  def _compile_transition_map(self, waveforms, clock_transitions, t_max):
    """
    Convert the input waveforms from being channel-indexed to being
    timestamp-indexed.

    :param waveforms: the dict of waveforms from the processor engine
    :param clock_transitions: the dict of required clock transitions from the
                              processor engine
    :param t_max: the total duration of the sequence in units of time.

    :return: a dict(timestamp: {channel: value})
    """
    unit_time = 5*unit.ns
    transition_map = {}

    base_clk = self.minimum_period
    base_clk_cfg = clock_transitions.pop('InternalClock', None)
    if base_clk_cfg is not None:
      # check to see that Arbwave believes clock to match our minimum_period
      assert int(round(base_clk_cfg['dt'] / unit_time)) == base_clk, \
        'bbb.Timing: Arbwave gave internal clock ({}) mismatched to ' \
        'minimum-period ({})' \
        .format(int(round(base_clk_cfg['dt'] / unit_time)), base_clk)

    # first reformat the waveforms: this is straightforward
    for channel, groups in waveforms.items():
      for _, (encoding, transitions) in groups.items():
        # encoding is currently ignored (i.e. not defined) for digital
        # channel data
        for timestamp, value in transitions:
          transition_map.setdefault(timestamp*base_clk, {})[channel] = value

    # then add the clock transitions
    for channel, cfg in clock_transitions.items():
      # calculate the time in units if `unit_time`
      period = int(round(cfg['dt'] / unit_time))
      for edge in cfg['transitions']:
        edge *= period # rescale from dt to `unit_time` units

        # add clock edges to the transtion map
        # FIXME: it would not be too hard to support inverted channels...
        transition_map.setdefault(edge, {})[channel] = True
        transition_map.setdefault(edge + period//2, {})[channel] = False

    # add a dummy transition to the end to finish the sequence
    # convert to #minimum_period#s, then to unit_time
    ts_max = int(round(t_max / (base_clk * unit_time))) * base_clk
    ts_max = max([max(transition_map.keys()) + base_clk, ts_max])
    transition_map[ts_max] = {}

    return transition_map
