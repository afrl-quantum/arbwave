# vim: ts=2:sw=2:tw=80:nowrap

class CallFunc:
  """
  Create a function wrapper that sends the same arguments to the function
  everytime the wrapper is called.
  """
  def __init__(self,C,A,K):
    """
    Create the wrapper of the function (C) with the position arguments A and
    keyword arguments K.
    """
    assert callable(C), 'expected callable: ' + repr(C)
    self.C = C
    self.A = A
    self.K = K
  def __call__(self):
    self.C( *self.A, **self.K )

