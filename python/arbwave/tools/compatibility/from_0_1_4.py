# vim: ts=2:sw=2:tw=80:nowrap
import re
from .register import register_converter

def to_0_1_5( vardict ):
  """
  Convert configuration data from version 0.1.4 to 0.1.5
  """
  from ...processor import messages as msg
  msg.info('Converted configuration file from version '
             '<span color="red">0.1.4</span> to version '
             '<span color="blue">0.1.5</span>\n' \
           '<span color="green">Changes:</span>' \
           '  Viewpoint slave clocks now require divider parameter.\n' \
           +(' '*20)+'All relevant clocks set to default value of' \
             ' <span color="blue">1</span>\n'
           , buttons='ok', ignore_result=True)

  for clk in vardict['clocks']:
    if re.match('vp/Dev[0-9]*/[A-D]/[0-9]*', clk):
      vardict['clocks'][clk]['divider'] = {'type': int, 'value': 1}
  return vardict

register_converter( '0.1.4', '0.1.5', to_0_1_5 )
