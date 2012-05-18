# vim: ts=2:sw=2:tw=80:nowrap

import sys
import viewpoint as vp

from ...device import Device as Base
from ....float_range import float_range


class Device(Base):
  def __init__(self, prefix, board_number, simulated=False):
    Base.__init__(self, name='{}/Dev{}'.format(prefix,board_number))
    self.simulated = simulated

    if not simulated:
      self.board = vp.Board(
        # default to *all* inputs so that all are high-impedance
        vp.Config('in', range(0,64) ),
        board=board_number,
      )
    elif board_number > 0:
      raise IndexError('Only one board in simulated mode.')
    else:
      self.board = board_number

    self.config = {
      'number-input-ports' : 0,
    }


  def set_output(self, data):
    if not self.simulated:
      self.board.set_output( data )
    else:
      print '{}.{}.set_output({})'.format(self.prefix(), self.board, data)


  def get_config_template(self):
    return {
      'number-input-ports' : {
        'default' : 0,
        'type'    : int,
        'range'   : xrange(5),
      },
      'output-scan_rate' : {
        'default' : vp.config.valid_settings['out']['scan_rate'],
        'type'    : float,
        'range'   : float_range(0.0,40e6),
      },
      'output-clock' : {
        'default' : vp.config.valid_settings['out']['clock'],
        'type'    : int,
        'range'   : [(vp.CLCK_INTERNAL,'internal'),
                     (vp.CLCK_EXTERNAL,'external--pin 20'),
                     (vp.CLCK_TRIG_0,'TRIG/0 (backplane)'),
                     (vp.CLCK_OCXO, 'internal OCXO option'),
                    ],
      },
      'output-divider' : {
        'default' : vp.config.valid_settings['out']['divider'],
        'type'    : int,
        'range'   : xrange(sys.maxint),
      },
      'output-trig_type' : {
        'default' : vp.config.valid_settings['out']['trig_type'],
        'type'    : int,
        'range'   : [ (vp.STRTTYPE_LEVEL, 'level'),
                      (vp.STRTTYPE_EDGETOEDGE, 'Edge to edge'),
                      (vp.STRTTYPE_EDGE, 'Edge'),
                    ],
      },
      'output-trig_edge' : {
        'default' : vp.config.valid_settings['out']['trig_edge'],
        'type'    : int,
        'range'   : [ (vp.TRIG_RISING, 'rising'),
                      (vp.TRIG_FALLING, 'falling'),
                    ],
      },
      'output-trig_source' : {
        'default' : vp.config.valid_settings['out']['trig_source'],
        'type'    : int,
        'range'   : [ (vp.STRT_NONE, 'none'),
                      (vp.STRT_EXTERNAL, 'external--pin 24'),
                      (vp.STRT_TRIG_2, 'TRIG/2 (backplane)'),
                      (vp.STRT_PXI_STAR, 'PXI Star trigger'),
                    ],
      },
      'output-stop_edge' : {
        'default' : vp.config.valid_settings['out']['stop_edge'],
        'type'    : int,
        'range'   : [ (vp.TRIG_RISING, 'rising'),
                      (vp.TRIG_FALLING, 'falling'),
                    ],
      },
      'output-stop' : {
        'default' : vp.config.valid_settings['out']['stop'],
        'type'    : int,
        'range'   : [ (vp.STOP_NONE, 'none'),
                      (vp.STOP_EXTERNAL, 'external--pin 25'),
                      (vp.STOP_TRIG_3_IN, 'TRIG/3 (backplane)'),
                      (vp.STOP_OUTPUT_FIFO, 'FIFO exhausted'),
                    ],
      },

      'input-scan_rate' : {
        'default' : vp.config.valid_settings['in']['scan_rate'],
        'type'    : float,
        'range'   : float_range(0.0,40e6),
      },
      'input-clock' : {
        'default' : vp.config.valid_settings['in']['clock'],
        'type'    : int,
        'range'   : [(vp.CLCK_INTERNAL,'internal'),
                     (vp.CLCK_EXTERNAL,'external--pin 20'),
                     (vp.CLCK_TRIG_0,'TRIG/0 (backplane)'),
                     (vp.CLCK_OCXO, 'internal OCXO option'),
                    ],
      },
      'input-divider' : {
        'default' : vp.config.valid_settings['in']['divider'],
        'type'    : int,
        'range'   : xrange(sys.maxint),
      },
      'input-trig_type' : {
        'default' : vp.config.valid_settings['in']['trig_type'],
        'type'    : int,
        'range'   : [ (vp.STRTTYPE_LEVEL, 'level'),
                      (vp.STRTTYPE_EDGETOEDGE, 'Edge to edge'),
                      (vp.STRTTYPE_EDGE, 'Edge'),
                    ],
      },
      'input-trig_edge' : {
        'default' : vp.config.valid_settings['in']['trig_edge'],
        'type'    : int,
        'range'   : [ (vp.TRIG_RISING, 'rising'),
                      (vp.TRIG_FALLING, 'falling'),
                    ],
      },
      'input-trig_source' : {
        'default' : vp.config.valid_settings['in']['trig_source'],
        'type'    : int,
        'range'   : [ (vp.STRT_NONE, 'none'),
                      (vp.STRT_EXTERNAL, 'external--pin 24'),
                      (vp.STRT_TRIG_2, 'TRIG/2 (backplane)'),
                      (vp.STRT_PXI_STAR, 'PXI Star trigger'),
                    ],
      },
      'input-stop_edge' : {
        'default' : vp.config.valid_settings['in']['stop_edge'],
        'type'    : int,
        'range'   : [ (vp.TRIG_RISING, 'rising'),
                      (vp.TRIG_FALLING, 'falling'),
                    ],
      },
      'input-stop' : {
        'default' : vp.config.valid_settings['in']['stop'],
        'type'    : int,
        'range'   : [ (vp.STOP_NONE, 'none'),
                      (vp.STOP_EXTERNAL, 'external--pin 25'),
                      (vp.STOP_TRIG_3_IN, 'TRIG/3 (backplane)'),
                      (vp.STOP_OUTPUT_FIFO, 'FIFO exhausted'),
                    ],
      },
    }
