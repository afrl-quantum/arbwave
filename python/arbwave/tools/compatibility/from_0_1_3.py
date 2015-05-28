# vim: ts=2:sw=2:tw=80:nowrap
from .register import register_converter

def to_0_1_4( vardict ):
  """
  Convert configuration data from version 0.1.3 to 0.1.4
  """
  from ...processor import messages as msg
  msg.warn('Converted configuration file from version '
             '<span color="red">0.1.3</span> to version '
             '<span color="blue">0.1.4</span>\n' \
           '<span color="green">Changes:</span>\n' \
           '  1) For loop nesting now explicit.\n'
           '  2) Sibling (consecutive) for loops now possible.\n'
           '<span color="red">' \
           'ALL FOR LOOP VARIABLES MUST BE RE-NESTED EXPLICITLY' \
           '</span>\n' \
           , buttons='ok', ignore_result=True)
  return vardict

register_converter( '0.1.3', '0.1.4', to_0_1_4 )
