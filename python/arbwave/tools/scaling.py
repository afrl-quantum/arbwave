# vim: ts=2:sw=2:tw=80:nowrap

import numpy as np

from .eval import evalIfNeeded

def calculate( scaling, units, offset, globals, return_range=False ):
  U = evalIfNeeded(units, globals)

  # we allow the user to comment out the offset (instead of just clearing it)
  if offset is not None:
    offset = offset.partition('#')[0].strip()

  # now with commented portion ignored, calculate the offset
  if offset:
    offset = evalIfNeeded(offset, globals)
    # ensure proper units
    U.unitsMatch( offset, 'Scaling offset must have proper units' )
    offset /= U
  else:
    offset = 0

  D = dict()
  for x,y in scaling:
    if x and y:
      yval = evalIfNeeded(y,globals)
      xval = evalIfNeeded(x,globals)

      try: # assume iterable first
        assert len(xval) == len(yval), \
          'Sequence entries X and Y must have same length'
        XVALS = xval
        YVALS = yval
      except TypeError: #make these into an array
        XVALS = [xval]
        YVALS = [yval]

      for xi, yi in zip( XVALS, YVALS ):
        assert 'units' not in dir(xi), \
          'expected unitless scaler in voltage entries'
        assert 'units' not in dir(yi), \
          'expected unitless scaler in output entries'
        D[xi] = float(yi - offset)

  if return_range:
    XVALS = D.keys()
    return min(XVALS), max(XVALS)

  # make sure that the order of data is correct
  D = sorted(D.items(), key=lambda v: v[0]) # sort by x
  D = np.array(D)
  return D
