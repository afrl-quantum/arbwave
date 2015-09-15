# vim: ts=2:sw=2:tw=80:nowrap
import re
from .register import register_converter

def to_0_1_8( vardict ):
  """
  Convert configuration data from version 0.1.7 to 0.1.8
  """
  from ...processor import messages as msg
  msg.info(
    'Converted configuration file from version '
    '<span color="red">0.1.7</span> to version '
    '<span color="blue">0.1.8</span>\n'
    '<span color="green">Changes:</span>'
    '  Backend connections allow local and/or remote access.\n'
    , buttons='ok', ignore_result=True
  )

  vardict['hosts'] = {'__default__': 'local', 'local': 'localhost'}
  return vardict

register_converter( '0.1.7', '0.1.8', to_0_1_8 )
