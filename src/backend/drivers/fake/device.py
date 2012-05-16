# vim: ts=2:sw=2:tw=80:nowrap

from ...device import Device as Base
from ....float_range import float_range


class Device(Base):
  def get_config_template(self):
    return {
      'bool'       : {
        'default' : True,
        'type'    : bool,
        'valid'   : None,
      },
      'int'       : {
        'default' : 0,
        'type'    : int,
        'valid'   : xrange(5),
      },
      'float'     : {
        'default' : 42.24,
        'type'    : float,
        'valid'   : float_range(0.0,40e6),
      },
      'str'       : {
        'default' : 'a value',
        'type'    : str,
        'valid'   : None,
      },
      'intlist'   : {
        'default' : 0,
        'type'    : int,
        'valid'   : [(0,'internal'),
                     (1,'external--pin 20'),
                     (2,'TRIG/0 (backplane)'),
                     (3, 'internal OCXO option'),
                    ],
      },
      'fltlist'   : {
        'default' : 54.23,
        'type'    : float,
        'valid'   : [54.23, (23,'some nice number'), 323.32],
      },
      'strlist'   : {
        'default' : 'value 0',
        'type'    : str,
        'valid'   : [ 'rising',
                      ('falling', 'to somewhere'),
                      ('lost', 'anywhere'),
                    ],
      },
    }