#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


from itertools import izip
import bbb.ad9959

from base import Device as Base

CHARGE_PUMP = bbb.Dict(bbb.ad9959.regs.FR1.CHARGE_PUMP)
CHARGE_PUMP.pop('Default')

class Device(Base, bbb.ad9959.Device):
  """
  DDS Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid):
    # this opens connection to firmware and also resets device; the system clock
    # parameters will have to be set up.
    super(Device,self).__init__(hostid, 'dds')
    self.assert_sw_fw_compatibility()
    self.reset()
    self.powered = True # turn the power on


  def set_sysclk_float(self, refclk, sysclk, charge_pump):
    refclk_MHz = int(refclk / 1e6) # must be in MHz
    sysclk_MHz = int(sysclk / 1e6) # must be in MHz
    charge_pump = CHARGE_PUMP['_'+charge_pump]
    super(Device,self).set_sysclk(refclk_MHz, sysclk_MHz, charge_pump)


  def get_sysclk_float(self):
    D = super(Device,self).get_sysclk()
    D.sysclk = D.pop('sysclk_MHz') * 1e6
    D.refclk = D.pop('refclk_MHz') * 1e6
    # convert the charge_pump value into a nice string representation, but drop
    # the '_' prefix
    D.charge_pump = CHARGE_PUMP.reverse()[D.charge_pump][1:]
    # convert this to standard dict to more easily get across Pyro boundaries
    return dict(D)


  def get_charge_pump_values(self):
    """
    Return a list of string representations for all possible PLL charge pump
    values.
    """
    # remove the '_'_ prefix
    return tuple(v[1:] for v in CHARGE_PUMP.iterkeys())


  def set_output(self, values):
    """
    Immediately force the output on several channels; all others are
    unchanged.

    :param values: the channels to set. May be a dict of { <channel>: <value>},
                   or a list of [ (<channel>, <value>), ...] tuples or something
                   equivalently coercable to a dict
    """
    if not isinstance(values, dict):
      values = dict(values)

    for ch, val in values.iteritems():
      ch = int(ch)
      assert 0 <= ch <= 3, \
        '{}.set_output:  invalid channel number [{}]'.format(self, ch)
      self.set_frequency(val, 1 << ch)


  def set_waveforms(self, waveforms, n_chans):
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
    :param t_max: the maximum duration of any channel
    :param continuous: bool of continuous or single-shot mode
    :param n_chans: The number of channels configured for output.  This is used
                    to define the base time unit using get_minimum_period(...).
    """
    W = self.convert_waveforms(waveforms, n_chans)
    self.load_waveform(W) # impl'd in bbb.ad9959.Device

  def convert_waveforms(self, waveforms, n_chans):
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
    :param t_max: the maximum duration of any channel
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
    dt = max(self.get_minimum_period(n_chans).itervalues()) * 5e-9

    transitions_map = dict() # timestamp -> dict(ch->op)
    for ch, wfm in waveforms.iteritems():
      ch = int(ch)

      for wfe_path, (encoding, wfe) in wfm.iteritems():

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
          # FIXME:  This really needs to be tested more thoroughly
          t0        = wfe[0][0]
          t1        = wfe[1][0]
          freq0     = wfe[0][1]
          freq1     = wfe[1][1]
          freq_last = wfe[-1][1]
          SLOPE = (freq1 - freq0) / float(dt*(t1 - t0))
          DT_synthetic = ((freq_last - freq0) / SLOPE)

          transitions_map.setdefault(t0, {})[ch] = \
            ('set_frequency_ramp', freq0, freq_last, DT_synthetic)

          # Subsequent components only update the slope.
          for (t0,f0), (t1,f1) in izip(wfe[1:-1], wfe[2:]): # skip first and last
            transitions_map.setdefault(t0, {})[ch] = \
              ('update_frequency_ramp', f0, f1, (t1-t0)*dt)

          # now finally, we add in the last step
          transitions_map.setdefault(wfe[-1][0], {})[ch] = \
            ('set_frequency', freq_last)
        else:
          raise RuntimeError(
            'bbb.dds: Unsupported waveform encoding [{}]'.format(encoding)
          )

    waveform = transitions_map.items()
    waveform.sort(key = lambda (timestep, data): timestep)
    return [wi[1] for wi in waveform]


if __name__ == '__main__':
  import sys, _main_controller_loop as Main

  Main.main(Device)
  sys.exit()
