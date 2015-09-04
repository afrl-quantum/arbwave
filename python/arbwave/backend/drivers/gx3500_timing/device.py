# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Logical device for GX3500 timing board.

@author: bks
"""

from copy import deepcopy
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
            self.board = timingboard.TimingBoard(address)
        else:
            self.board = object() # timingboard_sim.TimingBoard(address)
