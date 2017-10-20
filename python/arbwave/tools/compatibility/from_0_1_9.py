# vim: ts=2:sw=2:tw=80:nowrap
import re
from .register import register_converter

def to_1_0_0( vardict ):
  """
  Convert configuration data from version 0.1.9 to 1.0.0
  """
  from ...processor import messages as msg
  msg.info(
    'Converted configuration file from version '
    '<span color="red">0.1.9</span> to version '
    '<span color="blue">1.0.0</span>\n'
    '<span color="green">Changes:</span>\n'
    '  Channels now permit plot scaling and offset.\n'
    '  Ensuring each channel config includes plot scaling/offset...\n'
    , buttons='ok', ignore_result=True
  )

  for chlabel, chcfg in vardict['channels'].iteritems():
    chcfg.setdefault('plot_scale_factor', 1.0)
    chcfg.setdefault('plot_scale_offset', 0.0)
  return vardict

register_converter( '0.1.9', '1.0.0', to_1_0_0 )
