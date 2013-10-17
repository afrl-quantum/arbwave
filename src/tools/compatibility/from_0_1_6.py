# vim: ts=2:sw=2:tw=80:nowrap
import re
from .register import register_converter

def to_0_1_7( vardict ):
  """
  Convert configuration data from version 0.1.6 to 0.1.7
  """
  from ...processor import messages as msg
  msg.info('Converted configuration file from version '
             '<span color="red">0.1.6</span> to version '
             '<span color="blue">0.1.7</span>\n' \
           '<span color="green">Changes:</span>' \
           '  Analog channel scalings now have offset.\n' \
           , buttons='ok', ignore_result=True)

  for cconf in vardict['channels'].values():
    cconf['offset'] = None
  return vardict

register_converter( '0.1.6', '0.1.7', to_0_1_7 )
