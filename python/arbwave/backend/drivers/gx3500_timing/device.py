# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Logical device for GX3500 timing board.

@author: bks
"""

import copy
#from marvin import timingboard, timingboard_sim
from logging import error, warn, debug, log, DEBUG, INFO
import time

from ...device import Device as Base
from ....tools.float_range import float_range
from ....tools.signal_graphs import nearest_terminal


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
        if self.clocks == clocks:
            return
        self.clocks = copy.deepcopy(clocks)

        warn('gx3500: Device.set_clocks() not implemented')

