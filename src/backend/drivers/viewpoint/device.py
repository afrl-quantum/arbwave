# vim: ts=2:sw=2:tw=80:nowrap

import viewpoint as vp

from ...device import Device as Base
from ....float_range import float_range


class Device(Base):
  def __init__(self, board_number):
    Base.__init__(self, name=board_number)

    self.board = vp.Board(
      # default to *all* inputs so that all are high-impedance
      vp.Config('in', range(0,64) ),
      board=board_number,
    )

    self.config = {
      'number-input-ports' : 0,
    }


  def get_config_template(self):
    return {
      'number-input-ports' : {
        'default' : 0,
        'type'    : int,
        'valid'   : xrange(5),
      },
      'scan_rate' : {
        'default' : vp.config.valid_settings['out']['scan_rate'],
        'type'    : float,
        'valid'   : float_range(0.0,40e6),
      },
    }
