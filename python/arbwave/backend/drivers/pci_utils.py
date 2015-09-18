# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-

"""
Utility functions for dealing with PCI/PXI busses.

@author: bks
"""


import os


class PciBusSearch(object):
    """
    A query against the PCI bus database to find all cards with a given
    manufacturer and (optionally) class and/or device.
    
    NOTE: this is linux-only for now!
    """
    
    def __init__(self, manufacturer, pciclass=None, device=None):
        """
        Create a query.
        
        :param manufacturer: the numerical manufacturer code
        :param pciclass: the numerical PCI class code, or None to match
                         all classes
        :param device: the numerical PCI device code, or None to match all
                         all devices
        """
        self.manufacturer = '"{:x}"'.format(manufacturer)
        self.pciclass = '"{:x}"'.format(pciclass) if pciclass is not None else None
        self.device = '"{:x}"'.format(device) if device is not None else None
        self._loaded = False

    @property
    def result(self):
        """
        The result of executing the query.
        
        :return: a list of (bus, slot, function) numeric tuples
        """

        if self._loaded:
            return self._result

        with os.popen('lspci -m -n', 'r') as lspci:
            lines = lspci.readlines()

        r = []

        for line in lines:
            parts = line.split(' ')
            addr, pciclass, manufacturer, device = parts[:4]
            if (manufacturer == self.manufacturer and
               (self.pciclass is None or pciclass == self.pciclass) and
               (self.device is None or device == self.device)):
                bus, devfn = addr.split(':')
                dev, fn = devfn.split('.')
                r.append((bus, dev, fn))

        self._result = r
        self._loaded = True
        return r
