# vim: ts=2:sw=2:tw=80:nowrap
from ...channels import *
from ... import channels as base
from ....float_range import float_range

class Timing(base.Timing):
  """Test timing channel class"""

  def get_config_template(self):
    return {
      'bool'       : {
        'default' : True,
        'type'    : bool,
        'range'   : None,
      },
      'int'       : {
        'default' : 0,
        'type'    : int,
        'range'   : xrange(5),
      },
      'float'     : {
        'default' : 42.24,
        'type'    : float,
        'range'   : float_range(0.0,40e6),
      },
      'str'       : {
        'default' : 'a value',
        'type'    : str,
        'range'   : None,
      },
      'intlist'   : {
        'default' : 0,
        'type'    : int,
        'range'   : [(0,'internal'),
                     (1,'external--pin 20'),
                     (2,'TRIG/0 (backplane)'),
                     (3, 'internal OCXO option'),
                    ],
      },
      'fltlist'   : {
        'default' : 54.23,
        'type'    : float,
        'range'   : [54.23, (23,'some nice number'), 323.32],
      },
      'strlist'   : {
        'default' : 'value 0',
        'type'    : str,
        'range'   : [ 'rising',
                      ('falling', 'to somewhere'),
                      ('lost', 'anywhere'),
                    ],
      },
    }
