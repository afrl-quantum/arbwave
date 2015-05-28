# vim: ts=2:sw=2:tw=80:nowrap
from .register import register_converter

def to_0_1_3( vardict ):
  """
  Convert configuration data from version 0.1.2 to 0.1.3
  """
  from ...processor import messages as msg
  msg.info('Converted configuration file from version '
             '<span color="red">0.1.2</span> to version '
             '<span color="blue">0.1.3</span>\n' \
           '<span color="green">Changes:</span>' \
           '  For loop <span color="red">min/max/step</span> converted to\n' \
           +(' '*20)+'<span color="blue">arange(min,max,step)</span>\n'
           , buttons='ok', ignore_result=True)

  for k in vardict['runnable_settings']:
    if not k.endswith(':  Loop'): continue
    for p in vardict['runnable_settings'][k]['parameters']:
      p['iterable'] = 'arange({},{},{})' \
        .format(p.pop('min'), p.pop('max'), p.pop('step'))
  return vardict

register_converter( '0.1.2', '0.1.3', to_0_1_3 )
