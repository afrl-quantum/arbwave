# vim: ts=2:sw=2:tw=80:nowrap
"""
Lookup table of known (kernel,board,subdev_type) tuples to capabilities for subdevices.
The board_id and subdev_type elements of the tuple may be a wild card ('*').

The capabilities that are cataloged currently are:
  - finite_end_clock
    This is an indicator of whether the particular subdevice requires an extra
    clock at the end of the buffer sequence in order to signal the software that
    the sequence has finished.
"""

table = {
  ('ni_pcimio','*','ao') : dict(
    finite_end_clock = True,
  ),

  # default entry
  'default' : dict(
    finite_end_clock = False,
  ),
}

def get(kernel_module, board_name, subdev_type):
  if   (kernel_module, board_name, subdev_type) in table:
    return table.get((kernel_module, board_name, subdev_type))
  elif (kernel_module, board_name, '*') in table:
    return table.get((kernel_module, board_name, '*'))
  elif (kernel_module, '*', subdev_type) in table:
    return table.get((kernel_module, '*', subdev_type))
  elif (kernel_module, '*', '*') in table:
    return table.get((kernel_module, '*', '*'))

  return table.get('default') # return the default
