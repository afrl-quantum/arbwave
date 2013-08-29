# vim: ts=2:sw=2:tw=80:nowrap
import re
from .register import register_converter

def to_0_1_6( vardict ):
  """
  Convert configuration data from version 0.1.5 to 0.1.6
  """
  from ...processor import messages as msg
  msg.info('Converted configuration file from version '
             '<span color="red">0.1.5</span> to version '
             '<span color="blue">0.1.6</span>\n' \
           '<span color="green">Changes:</span>' \
           '  Multiple waveforms now possible.\n' \
           , buttons='ok', ignore_result=True)

  vardict['waveforms'] = {
    'current_waveform' : 'Default',
    'waveforms' : {
      'Default' : vardict['waveforms'],
    },
  }
  return vardict

register_converter( '0.1.5', '0.1.6', to_0_1_6 )
