# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Some details of the DDS front end implementation done here in order to allow
these details to be used by the simulation.
"""

class Details(object):
  def set_waveforms(self, waveforms, n_chans, transitions):
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
    :param continuous: bool of continuous or single-shot mode
    :param n_chans: The number of channels configured for output.  This is used
                    to define the base time unit using get_minimum_period(...).
    """
    W = self.convert_waveforms(waveforms, n_chans, transitions)
    self.load_waveform(W) # impl'd in bbb.ad9959.Device

  def convert_waveforms(self, waveforms, n_chans, transitions):
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
    :param continuous: bool of continuous or single-shot mode
    :param n_chans: The number of channels configured for output.  This is used
                    to define the base time unit using get_minimum_period(...).
    """
    # has to convert this
    # waveforms={
    #   '1': {
    #     (-1,): ('step', [(0, 2898.289828982898)]),
    #     (2, 4): ('step', [(33400, 3098.109810981098)]),
    #   },
    #   '0': {
    #     (2, 3): ('linear', [(40067, 33299999.999999993)), (46732, 4000000.0000000005)]),
    #     (-1,): ('step', [(0, 50000000.0)]),
    #     (2, 2): ('step', [(33400, 33299999.999999993)]),
    #   },
    # }
    #
    # to
    #
    # [
    #   { # timestep 1
    #    #ch: (op, op_args,...)
    #     0 : ('set_frequency', 33e6),
    #     1 : ('set_frequency', 22e6),
    #     2 : ('set_frequency', 12e6),
    #     3 : ('set_frequency', 92e6),
    #   },
    #   { # timestep 2
    #     1 : ('set_frequency', 45e6),
    #     2 : ('set_frequency_ramp', 12e6, 77e6, .5),
    #   },
    #   { # timestep 3
    #     2 : ('update_frequency_ramp', 50e6, 77e6, 1),
    #   },
    # ]

    # integer time is given in these units.
    # Note that I am not using physicsal.units pacakge since I'm trying to limit
    # brining _any_ packages into the code that runs on the beaglebone that
    # isn't *entirely* necessary.
    dt = max(self.get_minimum_period(n_chans).values()) * 5e-9

    transitions_map = dict() # timestamp -> dict(ch->op)
    for ch, wfm in waveforms.items():
      ch = int(ch)

      for wfe_path, (encoding, wfe) in wfm.items():

        if encoding == 'step':
          for timestamp, value in wfe:
            transitions_map.setdefault(timestamp, {})[ch] = \
              ('set_frequency', value)
        elif encoding == 'linear':
          # create the first component to set beginning/ending frequencies and
          # initial slope.  The initial slope is finagled into being correct by
          # choosing a DT that ensures the slope is computed correctly.  The
          # actual time over which the first element endures is simply dependent
          # on the external update pulse.
          t0        = wfe[0][0]
          t1        = wfe[1][0]
          freq0     = wfe[0][1]
          freq1     = wfe[1][1]
          freq_last = wfe[-1][1]

          transitions_map.setdefault(t0, {})[ch] = \
            ('set_frequency_ramp', freq0, freq1, freq_last, (t1-t0)*dt)

          # Subsequent components only update the slope.
          for (t0,f0), (t1,f1) in zip(wfe[1:-1], wfe[2:]): # skip first and last
            transitions_map.setdefault(t0, {})[ch] = \
              ('update_frequency_ramp', f0, f1, (t1-t0)*dt)

          # now finally, we add in the last step
          transitions_map.setdefault(wfe[-1][0], {})[ch] = \
            ('set_frequency', freq_last)
        else:
          raise RuntimeError(
            'bbb.dds: Unsupported waveform encoding [{}]'.format(encoding)
          )

    if set(transitions_map) != set(transitions):
      # FIXME:  We need to just add in a "dummy" instruction that does nothing.
      # The problem is that we already used this "dummy" instruction as the end
      # of the waveform.  We will need to use one of the reserved bits to mark
      # the end of the waveform and change the meaning of no updates to just
      # be a no-operation (but not the end of the waveform).
      raise RuntimeError(
        'DDS cannot currently share clock source with other devices')

    waveform = list(transitions_map.items())
    waveform.sort(key = lambda timestep_data: timestep_data[0])
    return [wi[1] for wi in waveform]
