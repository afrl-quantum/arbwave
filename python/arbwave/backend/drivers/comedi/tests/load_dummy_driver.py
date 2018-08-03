#!/usr/bin/env python3
# vim: ts=2:sw=2:tw=80:nowrap
"""
Load the dummy comedi driver--meant for demonstration purposes.
"""
import os

print('loading dummy comedi kernel module...')
os.system('sudo modprobe comedi comedi_num_legacy_minors=4')
os.system('sudo modprobe comedi_test')
print('configuring dummy on /dev/comedi0...')
os.system('sudo comedi_config -v /dev/comedi0 comedi_test')
