# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Logical device for GX3500 timing board.

@author: bks
"""

import copy
#from marvin import timingboard, timingboard_sim
from logging import error, warn, debug, log, DEBUG, INFO
import numpy as np
import time

from ...device import Device as Base
from ....tools.float_range import float_range
from ....tools.signal_graphs import nearest_terminal


_port_bases = {'A': 0, 'B': 32, 'C': 64, 'D': 96}
_group_bases = {'E': 0, 'F': 4, 'G': 8, 'H': 12, 'J': 16, 'K': 20, 'L': 24, 'M': 28}

def _port_bit(path_or_line):
    """
    Convert a path or line number to a (port_nr, bit_nr) bit addess. The
    path should just be the tail port/group#bit part (e.g. A/G2)

    :return: the (port_nr, bit_nr) tuple such that 
             (ports[port_nr] & (1 << bit_nr)) >> bit_nr
             will extract the referenced bit.
    """
    if type(path_or_line) == str:
        assert len(path_or_line) == 4, \
          'Path must be of the form A/E0'
        port_nr = _port_bases[path_or_line[0]]
        bit_nr = _group_bases[path_or_line[2]] + int(path_or_line[3])
    else:
        port_nr = path_or_line / 32
        bit_nr = path_or_line % 32

    return (port_nr, bit_nr)

class Device(Base):
    """
    The logical Device for a single instance of the GX3500 timing board.
    """

    def __init__(self, driver, address, simulated=False):
        """
        Instantiate a Device.
        
        :param address: the board PCI bus/slot address
        :param simulated: if True, use a simulated version of the timing board
        """
        super(Device,self).__init__(name='{}/Dev_{:04x}'.format( driver, address ))
        self.driver = driver

        if not simulated:
            from marvin import timingboard
            self.board = timingboard.TimingBoard(address)
        else:
            from marvin import timingboard_sim
            self.board = timingboard_sim.TimingBoard(address)

        self.possible_clock_sources = [
            '{dev}/Internal_PXI_10_MHz'.format(dev=self),
            '{dev}/Internal_XO'.format(dev=self)
        ]

        self.board_config = {
            'use_10_MHz': False,
            'external_trigger': True
        }

        self.clocks = None
        self.config = None
        self.signals = None
        self.ports = np.zeros((4,), dtype=np.uint32)
        self.set_output({}) # write the port values to the hardware

    def __del__(self):
        """
        Final cleanup.
        """
        self.board.command('STOP')

    def get_config_template(self):
        """
        Create the configuration template (the set of possible configuration
        parameters and their allowed values).

        :return: the configuration template
        """
        return {
            'clock': {
                'value': '{dev}/Internal_XO'.format(dev=self),
                'type': str,
                'range': self.possible_clock_sources
            },
            'hw_trigger': {
                'value': True,
                'type': bool,
                'range': None
            }
        }

    def set_config(self, config):
        """
        Set the internal configuration for the board. This
        does not include the sequence specification or the PXI routing.

        :param config: the configuration dictionary to be applied, compare
                       get_config_template()
        """
        debug('gx3500.Device({}).set_config(config={})'.format(self, config))
        valid_keys = set(self.get_config_template().keys())
        assert set(config.keys()).issubset(valid_keys), \
          'Unknown configuration keys for GX3500 timing board'

        if self.config == config:
            return

        if 'clock' in config:
            self.board_config['use_10_MHz'] = not 'Internal_XO' in config['clock']['value']
        if 'hw_trigger' in config:
            self.board_config['external_trigger'] = config['hw_trigger']['value'] == 1

        self.config = copy.deepcopy(config)

    def set_clocks(self, clocks):
        """
        Set which clock is controlling the board.

        :param clocks: a dict of {'clock/path': config_dict }
        """
        debug('gx3500.Device({}).set_clocks(clocks={})'.format(self, clocks))
        if self.clocks == clocks:
            return
        self.clocks = copy.deepcopy(clocks)

        warn('gx3500: Device.set_clocks() not implemented')

    def set_signals(self, signals):
        """
        Set the PXI routing bits.

        :param signals: a dict of { (src, dest) : config_dict} where src and
                        dest are both paths
        """
        debug('gx3500.Device({}).set_signals(signals={})'.format(self, signals))
        if self.signals == signals:
            return
        self.signals = copy.deepcopy(signals)

        skip_self = len(str(self)) + 1

        kwroutes = {}
        used_triggers = set()

        for src, dest in signals.iterkeys():
            if src.startswith( str(self) ) and 'TRIG' in dest:
                n = int(dest[-1])
                if n < 0 or n > 7:
                    raise ValueError('cannot route to ' + dest)
                if n in used_triggers:
                    raise ValueError('cannot route multiple channels to ' + dest)
                used_triggers.add(n)

                port, bit = _port_bit(src[skip_self:])
                kwroutes['pxi' + dest[-1]] = 32*port + bit

        self.board.set_pxi_routing(**kwroutes)

    def set_output(self, values):
        """
        Immediately force the output on several channels; all others are
        unchanged. Channels default to LOW on board initialization.

        :param values: the channels to set. May be a dict of { <channel>: bool},
                       or a list of [ (<channel>, bool), ...] tuples or something
                       equivalently coercable to a dict

        Channel names can be of the following forms:
          integer:
            between 0 and 127
          'port/group#line':
            port is one of [ABCD]; group is one of [EFGHJKLM],
            and line is between 0 and 3 (e.g. A/E2)
        """
        debug('gx3500.Device({}).set_output(values={})'.format(self, values))
        if not isinstance(values, dict):
            values = dict(values)

        for channel, val in values.iteritems():
            (port, bit) = _port_bit(channel)
            if val:
                self.ports[port] |= (1 << bit)
            else:
                self.ports[port] &= ~(1 << bit)

        self.board.set_defaults(*self.ports)
