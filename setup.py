#!/usr/bin/env python3

from setuptools import setup, find_packages
import os, sys

THIS_DIR = os.path.dirname( __file__ )
sys.path.insert(0, os.path.join(THIS_DIR, 'python'))

import arbwave.version

arbwave.version.write_version_file()

VERSION_FILE = os.path.relpath(arbwave.version.VERSION_FILE, THIS_DIR)
f = open('MANIFEST.in', 'w')
f.write('include {}\n'.format(VERSION_FILE))
f.write('graft python/arbwave\n')
f.close()

try :
  setup(
    name='arbwave',
    version=arbwave.version.version().partition('-g')[0],
    author='Spencer E. Olson',
    author_email='olsonse@umich.edu',
    description='Arbitrary Waveform Experimental Control',
    long_description=
      'Arbwave is part of an effort from the Air Force Research Laboratory '
      '(AFRL) Cold-Atoms group to develop a platform suitable for typical '
      'atomic physics experiments.  One of the goals of this effort is to '
      'provide a simple, consistent view and control of experimental timing '
      'parameters.  This software is released to the public in the form of an '
      'Open Source Software (OSS) project.  This is done with the intent and '
      'hope that the community in general can benefit from AFRL\'s work on '
      'Arbwave and to also foster collaboration for and sharing of special '
      'experimental expertise permeating throughout the scientific community.',
    url='https://github.com/afrl-quantum/arbwave',
    license='GPL3',
    packages=find_packages('python'),
    package_dir = {'' : 'python'},
    include_package_data=True,
    entry_points={
      'console_scripts': [
        'arbwave = arbwave:main',
        'arbwave-bbb_dds_controller = arbwave.backend.drivers.bbb.device.controller.dds:main',
        'arbwave-bbb_timing_controller = arbwave.backend.drivers.bbb.device.controller.timing:main',
      ],
    },
  )
finally:
  os.unlink('MANIFEST.in')
