# vim: ts=2:sw=2:tw=80:nowrap
import numpy as np

class float_range(object):
  def __init__(self, mn, mx, include_beginning=True, include_end=False,
               step=None):
    self.mn = mn
    self.mx = mx
    self.step = step
    self.include_beginning = include_beginning
    self.include_end = include_end


  def __contains__(self, v):
    if   self.include_beginning:
      if self.include_end:  return self.__contains_ib_ie__(v)
      else:                 return self.__contains_ib_xe__(v)
    else:
      if self.include_end:  return self.__contains_xb_ie__(v)
      else:                 return self.__contains_xb_xe__(v)

  def __str__(self):
    ib, ie = '', ''
    if self.include_end:
      ie = ',True'
      ib = ',{}'.format(self.include_beginning)

    if not self.include_beginning:
      ib = ',False'
    return 'float_range({},{}{}{})'.format(self.mn, self.mx, ib, ie)

  def __repr__(self):
    return str(self)

  def __contains_ib_ie__(self,v):
    return self.mn <= v and v <= self.mx

  def __contains_ib_xe__(self,v):
    return self.mn <= v and v < self.mx

  def __contains_xb_ie__(self,v):
    return self.mn < v and v <= self.mx

  def __contains_xb_xe__(self,v):
    return self.mn < v and v < self.mx

  def __iter__(self):
    class iter:
      def __init__(iself):
        iself.pos = 0
      def __iter__(iself):
        return iself
      def next(iself):
        i = iself.pos
        iself.pos += 1
        if i < 1:
          return self.mn
        elif i == 1:
          return self.mx
        else:
          raise StopIteration()
    return iter()


def xarange(i, f=None, step=1):
  """Something akin to xrange, except that for floats and syntax of arange"""
  if f is None:
    f = i
    i = 0
  while np.sign(step)*i < np.sign(step)*f:
    yield i
    i += step


if __name__ == '__main__':
  fr = float_range(0.1,5.1)
  assert min(fr) == 0.1, 'Min(float_range) failed'
  assert max(fr) == 5.1, 'Max(float_range) failed'
  assert .2 in fr, '"in float_range" failed'
  assert -.2 not in fr, '"in float_range" failed'
  assert 5.2 not in fr, '"in float_range" failed'
  print 'made it!'
