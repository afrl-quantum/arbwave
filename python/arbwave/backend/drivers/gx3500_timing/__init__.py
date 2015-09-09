# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Arbwave driver for our custom timing board implemented on the Marvin Test GX3500
FPGA PXI card.

@author: bks
"""

from device import Device
from marvin.exceptions import NotATimingBoard
import capabilities
from ...driver import Driver as Base
from .. import pci_utils
from ....tools.path import collect_prefix


class Driver(Base):
    """
    The driver for our GX3500-based 128-bit timing card.
    """
    prefix      = 'gxt'
    description = 'GX3500 Timing Card Driver'
    has_simulated_mode = True

    def __init__(self, *a, **kw):
        """
        Load the GX300 Timing Card driver and instantiate all available devices.
        """
        super(Driver,self).__init__(*a, **kw)

        # if we're simulating, just provide a single Device
        if self.simulated:
            board_addresses = [0x0b0f]
        else:
            MFR_MARVIN = 0x16e2
            DEV_GX3500 = 0x3500
            board_addresses = []
            search = pci_utils.PciBusSearch(manufacturer=MFR_MARVIN, device=DEV_GX3500)
            print 'Probing {} GX3500 devices...'.format(len(search.result))
            for bus, dev, fn in search.result:
                board_addresses.append(int(bus, 16) << 8 | int(dev, 16))

        # instantiate Devices for all the actual timing boards
        self.devices = {}
        for addr in board_addresses:
            try:
                dev = Device(self, addr, simulated=self.simulated)
                self.devices[str(dev)] = dev
            except NotATimingBoard:
                pass
        
        print 'Found {} timing boards.'.format(len(self.devices))

        self.digital_channels = capabilities.get_digital_channels(self.devices)
        self.timing_channels = capabilities.get_timing_channels(self.devices)
        self.signals = capabilities.get_routeable_backplane_signals(self.devices)

    def close(self):
        """
        Close all the devices and uninitialize.
        """
        del self.devices

    def get_devices(self):
        """
        Get the list of present devices.

        :return: a list of gx3500_timing.Device objects
        """
        return self.devices.values()

    def get_digital_channels(self):
        """
        Get the complete list of available digital channels.

        :return: a list of channels.Digital objects
        """
        return self.digital_channels

    def get_timing_channels(self):
        """
        Get the list of available timing channels.

        :return: a list of channels.Timing objects
        """
        return self.timing_channels

    def get_routeable_backplane_signals(self):
        """
        Get the list of signals which can be routed to the backplane.

        :return: a list of channels.Backplane objects
        """
        return self.signals

    def set_device_config( self, config, channels, shortest_paths ):
        """
        Set the device configurations for all devices controlled by this
        driver.

        :param config: a dict of {'device/path': config_dict }
        :param channels: ??
        :param shortest_paths: ??
        """
        for d,dev in self.devices.items():
            if d in config:
                dev.set_config( config.get(d,{}) )

    def set_clocks( self, clocks ):
        """
        Set the clock configurations for all devices controlled by this
        driver.

        :param clocks: a dict of {'device/path': clock_config_dict } where
                       clock_config_dict is a dict of { 'clock/path': config_dict }
        """
        clocks = collect_prefix(clocks, 0, 2)
        for d,dev in self.devices.items():
            if d in clocks:
                dev.set_clocks( clocks[d] )

    def set_signals( self, signals ):
        """
        Sets the signal routing for all devices controlled by this driver.

        :param signals: a dict of { (src, dest): config_dict }
        """
        signals = collect_prefix(signals, 0, 2, prefix_list=self.devices)
        for d,dev in self.devices.items():
           dev.set_signals( signals.get(d,{}) )

    def set_static(self, analog, digital):
        """
        Set immediate output values.

        :param analog: analog output value dicts
        :param digital: digital output value dicts
        """
        assert len(analog) == 0, 'GX3500 does not perform analog output'
        D = collect_prefix(digital, 0, 2, 2)
        for dev in D.items():
            self.devices[ dev[0] ].set_output( dev[1] )


    def set_waveforms(self, analog, digital, transitions,
                      t_max, end_clocks, continuous):
        pass