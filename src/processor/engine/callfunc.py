# vim: ts=2:sw=2:tw=80:nowrap

class CallFunc:
  def __init__(self,C,A,K):
    assert callable(C), 'expected callable: ' + repr(C)
    self.C = C
    self.A = A
    self.K = K
  def __call__(self):
    self.C( *self.A, **self.K )

