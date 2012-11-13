# vim: ts=2:sw=2:tw=80:nowrap
from .register import register_converter

def to_0_1_3( vardict ):
  """
  Convert configuration data from version 0.1.2 to 0.1.3
  """
  from ...processor import messages as msg
  msg.info('Converted configuration file from version '
           '<span color="red">0.1.2</span> to version '
           '<span color="blue">0.1.3</span>',
           buttons='ok', ignore_result=True)
  return vardict

register_converter( '0.1.2', '0.1.3', to_0_1_3 )
