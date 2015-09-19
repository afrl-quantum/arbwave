# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
import re
from .. import ctypes_comedi as clib

from .....tools.float_range import float_range
from .subdevice import Subdevice as Base

class Analog(Base):
  subdev_type = 'ao'


  default_range_min   = ['default-voltage-range','minimum','value']
  default_range_max   = ['default-voltage-range','maximum','value']
  reference_value     = ['reference','value']


  def get_config_template(self):
    template = Base.get_config_template(self)
    template.update( {
      'default-voltage-range' : {
        'minimum' : {
          'value' : -10.0,
          'type'  : float,
          'range' : float_range(-10.0, 10.0),
        },
        'maximum' : {
          'value' : 10.0,
          'type'  : float,
          'range' : float_range(-10.0, 10.0),
        },
      },

      'reference' : {
        'value' : clib.AREF_COMMON,
        'type' : int,
        'range' : [
          (clib.AREF_GROUND, 'Referenced to ground'),
          (clib.AREF_COMMON, 'Referenced to isolated \'common\' potential'),
          (clib.AREF_DIFF, 'Differential inputs/outputs (?)'),
          (clib.AREF_OTHER, 'Other reference (?: see comedi docs)'),
        ],
      },
    } )
    return template
