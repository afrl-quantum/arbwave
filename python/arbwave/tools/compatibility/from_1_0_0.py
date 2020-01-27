# vim: ts=2:sw=2:tw=80:nowrap
import re
from .register import register_converter

def to_1_2_0( vardict ):
  """
  Convert configuration data from version 1.0.0 to 1.2.0
  """
  from ...processor import messages as msg
  msg.info(
    'Converted configuration file from version '
    '<span color="red">1.0.0</span> to version '
    '<span color="blue">1.2.0</span>\n'
    '<span color="green">Changes:</span>\n'
    '  WARNING!!!\n'
    '  Default parameters for Value Expressions have changed:\n'
    '    expr_fmt : now defaults to "optimize" instead of "uniform"\n'
    '    expr_steps : now defaults to 100 instead of 10\n'
    '\n'
    '  Please ensure generated waveforms using Value Expressions meet\n'
    '  specific timing requirements.\n'
    , buttons='ok', ignore_result=True
  )

  return vardict

register_converter( '1.0.0', '1.2.0', to_1_2_0 )
