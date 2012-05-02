# vim: ts=2:sw=2:tw=80:nowrap

import viewpoint as vp

from ...device import Device as Base

class frange:
  def __init__(self,mn,mx):
    self.mn = mn
    self.mx = mx
  def __contains__(self,val):
    if self.mn <= val and val <= self.mx:
      return True
    return False


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
        'valid'   : frange(0.0,40e6),
      },
    }
