# vim: ts=2:sw=2:tw=80:nowrap

import viewpoint as vp

class Board(vp.Board):
  def __del__(self):
    self.close()

  def _open(self):
    pass

  def _load(self, nin, nout):
    pass

  def close(self):
    pass

  def _start_input(self):
    return self.configs['in']['scan_rate']

  def _setup_output(self):
    return self.configs['out']['scan_rate']

  def in_status(self):
    scans = vp.vtypes.dword()
    stat  = vp.vtypes.Status()
    return scans, stat

  def read(self, scans, status):
    return list( (vp.vtypes.word*scans)() ), status

  def in_stop(self):
    pass

  def out_stop(self):
    pass

  def out_start(self):
    pass

  def out_status(self):
    return vp.vtypes.dword(-1), vp.vtypes.Status()

  def write(self, transitions, status):
    print 'vp.{b}.write({t},...)'.format(b=self.board, t=transitions)
    return status

  def set_output(self, data):
    print 'vp.{b}.set_output({d})'.format(b=self.board, d=data)

  def get_last_inputs(self):
    return list( (vp.vtypes.word*8)() )

  def get_property(self, attr_id):
    print 'vp.{b}.get_property({a})'.format(b=self.board,a=attr_id)
    return None

  def set_property(self, attr_id, value):
    print 'vp.{b}.set_property({a},{v})'.format(b=self.board,a=attr_id,v=value)
