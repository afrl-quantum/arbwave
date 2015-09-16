# vim: ts=2:sw=2:tw=80:nowrap
import re
from .register import register_converter

def to_0_1_9( vardict ):
  """
  Convert configuration data from version 0.1.8 to 0.1.9
  """
  from ...processor import messages as msg
  msg.info(
    'Converted configuration file from version '
    '<span color="red">0.1.8</span> to version '
    '<span color="blue">0.1.9</span>\n'
    '<span color="green">Changes:</span>\n'
    '  Divider for viewpoint aperiodic timing channels now starts at 2 not 1.\n'
    '  Multiplying all viewpoint aperiodic clock dividers by 2...\n'
    , buttons='ok', ignore_result=True
  )

  for clk, clkcfg in vardict['clocks'].items():
    if re.match('vp/Dev[0-9]*/[A-D]/[0-9]*', clk):
      clkcfg['divider']['value'] *= 2
  return vardict

register_converter( '0.1.8', '0.1.9', to_0_1_9 )
