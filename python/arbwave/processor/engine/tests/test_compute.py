# vim: ts=2:sw=2:tw=80:nowrap
"""
Test compute(...)
"""

import unittest
from os import path
import copy
from physical import unit

import arbwave.options
import arbwave.backend
from arbwave.processor import default
import arbwave.processor.engine.send as send
from .. import compute

THIS_DIR = path.dirname( __file__ )

# typical import of physical units
physical_import = """\
from physical.constant import *
from physical.unit import *
from physical import unit
"""


def load_config_file():
  simple_config_path = path.join( THIS_DIR, *(
    [path.pardir]*5 + ['examples','simple_config.py']
  ))
  variables = dict()
  with open( simple_config_path ) as f:
    exec(compile(f.read(), simple_config_path, 'exec'), globals(), variables)
  return simple_config_path, variables


def load_simulated_drivers(host_defs):
  arbwave.options.simulated = True
  send.to_driver.hosts( host_defs )

def unload_simulated_drivers():
  arbwave.backend.unload_all()


class ComputeBase(unittest.TestCase):
  def setUp(self):
    # setup global variables
    # we are not yet executing L['global_script'] because I don't want
    # to have to import Arbwave fake module as well (yet).
    self.G = default.get_globals()
    exec(physical_import, self.G)

    self.simple_config_path, self.L = load_config_file()
    # some extra prep: processor does not like (analog|digital) prefixes
    # anymore:
    for chname, ch in self.L['channels'].items():
      if ch and ch['device']:
        ch['device'] = ch['device'].partition('/')[-1]

    load_simulated_drivers(self.L['hosts'])
    send.to_driver.clocks( self.L['clocks'] )
    send.to_driver.config( self.L['devices'], self.L['channels'],
                           self.L['signals'], self.L['clocks'], self.G )
    send.to_driver.signals( self.L['signals'] )

  def tearDown(self):
    unload_simulated_drivers()
    del self.simple_config_path
    del self.L


  static_answer = (
    {'ni': {
      'ni/Dev1/ao0': 10.0,
      'ni/Dev1/ao1': -5.0,
    }},
    {'vp': {
      'vp/Dev0/A/0': False,
    }},
  )
  def test_static(self):
    # setup global variables
    # we are not yet executing L['global_script'] because I don't want
    # to have to import Arbwave fake module as well (yet).
    vals = compute.static( self.L['devices'], self.L['channels'], self.G )

    self.assertEqual(vals,self.static_answer)



  waveform_answer = {
    'continuous' : {
      'analog' : {
        'ni': { # analog
          'ni/Dev1/ao0': {
            (-1,): ('step', [(0, 10.0)]),
            ( 1,): ('step', [(16667, 2.0)]),
            ( 2,): ('step', [
              (50000, 0.0),
              (50833, 0.499819992799712),
              (51666, 0.999639985599424),
              (52499, 1.499459978399136),
              (53332, 1.999279971198848),
              (54165, 2.4990999639985603),
              (54998, 2.998919956798272),
              (55831, 3.498739949597984),
              (56664, 3.998559942397696),
              (57497, 4.498379935197408),
              (58330, 4.9981999279971205),
              (59163, 5.498019920796832),
              (59996, 5.997839913596544),
              (60829, 6.497659906396256),
              (61662, 6.997479899195968),
              (62495, 7.49729989199568),
              (63328, 7.997119884795392),
              (64161, 8.496939877595103),
              (64994, 8.996759870394817),
              (65827, 9.496579863194528),
              (66660, 9.996399855994241),
              (66666, 10.0),
            ]),
            ( 3,): ('step', [
              (66667, 10.0),
              (67000, 8.303758540359429),
              (67333, 7.601152322716769),
              (67666, 7.062023609997738),
              (67999, 6.607517080718857),
              (68332, 6.207088789990217),
              (68665, 5.845073943326853),
              (68998, 5.512166934273844),
              (69331, 5.2023046454335375),
              (69664, 4.911275621078286),
              (69997, 4.636013525927218),
              (70330, 4.374203524527452),
              (70663, 4.124047219995475),
              (70996, 3.8841144416980384),
              (71329, 3.653245612783644),
              (71662, 3.4304850756655063),
              (71995, 3.2150341614377136),
              (72328, 3.006217295350048),
              (72661, 2.8034569681503068),
              (72994, 2.6062548935828236),
              (73327, 2.4141775799804335),
              (73660, 2.2268451142747008),
              (73993, 2.0439223252359664),
              (74326, 1.865111736705767),
              (74659, 1.690147886653708),
              (74992, 1.5187927017971425),
              (75325, 1.3508316975276191),
              (75658, 1.1860708299932108),
              (75991, 1.0243338685476875),
              (76324, 0.8654601871411315),
              (76657, 0.7093028957937032),
              (76990, 0.5557272502584478),
              (77323, 0.40460929086707503),
              (77656, 0.2558346714396311),
              (77989, 0.10929764679365304),
              (78322, 0.0),
              (78655, 0.0),
              (78988, 0.0),
              (79321, 0.0),
              (79654, 0.0),
              (79987, 0.0),
              (80320, 0.0),
              (80653, 0.0),
              (80986, 0.0),
              (81319, 0.0),
              (81652, 0.0),
              (81985, 0.0),
              (82318, 0.0),
              (82651, 0.0),
              (82984, 0.0),
              (83317, 0.0),
              (83332, 0.0),
            ]),
          },
          'ni/Dev1/ao1': {
            (-1,): ('step', [(0, -5.0)]),
          },
        },
      },
      'digital' : {
        'vp': { # digital
          'vp/Dev0/A/0': {
            (0,): ('step', [
              (200000, True),
              (399999, False),
            ]),
            (-1,): ('step', [ (0, False) ]),
          },
        },
      },
      'transitions' : { # clock_transitions
        'vp/Dev0/A/13': {'dt': 6e-07 * unit.s, 'transitions': {
          0, 83332, 67333, 68998, 70663, 72328, 73993, 75658, 77323, 78988,
          80653, 82318, 50833, 52499, 54165, 55831, 57497, 59163, 16667, 60829,
          62495, 67999, 64161, 69664, 65827, 71329, 72994, 74659, 76324, 77989,
          79654, 81319, 82984, 67000, 68665, 70330, 71995, 73660, 75325, 76990,
          78655, 80320, 81985, 50000, 51666, 67666, 53332, 69331, 54998, 70996,
          56664, 72661, 58330, 74326, 59996, 75991, 61662, 77656, 63328, 79321,
          64994, 80986, 66660, 82651, 66666, 66667, 68332, 69997, 71662, 73327,
          74992, 76657, 78322, 79987, 81652, 83317,
        }},
        'vp/Dev0/Internal_XO': {'dt': 5e-08 * unit.s, 'transitions': {
          200000, 0, 399999,
        }},
      },
      'clocks' : { # clocks
        'vp/Dev0/A/0': ('vp/Dev0/Internal_XO', 5e-08 * unit.s),
        'ni/Dev1/ao0': ('vp/Dev0/A/13', 6e-07 * unit.s),
        'ni/Dev1/ao1': ('vp/Dev0/A/13', 6e-07 * unit.s),
      },
      't_max' : 0.05*unit.s, # t_max
      'eval_cache' : {
        (0,): {'t': 0.01 * unit.s, 'dt': 0.01 * unit.s,
               'val': 'pulse(True, False)'},
        (1,): {'t': 0.010000199999999999 * unit.s,
               'dt': 0.009999599999999999 * unit.s,
               'val': '<2.0 kg m^2 / A s^3>'},
        (2,): {'t': 0.03 * unit.s, 'dt': 0.010000199999999999 * unit.s,
               'val': 'ramp(10.0*V, 1.0, 20, 0.0*V, None, '
                           '0.010000199999999999*s)'},
        (3,): {'t': 0.0400002 * unit.s, 'dt': 0.009999599999999999 * unit.s,
               'val': '-12.0*kilogram*meter**2*x**0.5/(ampere*second**3) + '
                      '10.0*kilogram*meter**2/(ampere*second**3)'},
      },
    },


    'non-continuous' : {
      'analog': {
        'ni': {
          'ni/Dev1/ao0': {
            (-2,): ('step', [(83333, 10.0)]),
            (-1,): ('step', [(0, 10.0)]),
            ( 1,): ('step', [(16667, 2.0)]),
            ( 2,): ('step', [
              (50000, 0.0),
              (50833, 0.499819992799712),
              (51666, 0.999639985599424),
              (52499, 1.499459978399136),
              (53332, 1.999279971198848),
              (54165, 2.4990999639985603),
              (54998, 2.998919956798272),
              (55831, 3.498739949597984),
              (56664, 3.998559942397696),
              (57497, 4.498379935197408),
              (58330, 4.9981999279971205),
              (59163, 5.498019920796832),
              (59996, 5.997839913596544),
              (60829, 6.497659906396256),
              (61662, 6.997479899195968),
              (62495, 7.49729989199568),
              (63328, 7.997119884795392),
              (64161, 8.496939877595103),
              (64994, 8.996759870394817),
              (65827, 9.496579863194528),
              (66660, 9.996399855994241),
              (66666, 10.0),
            ]),
            ( 3,): ('step', [
              (66667, 10.0),
              (67000, 8.303758540359429),
              (67333, 7.601152322716769),
              (67666, 7.062023609997738),
              (67999, 6.607517080718857),
              (68332, 6.207088789990217),
              (68665, 5.845073943326853),
              (68998, 5.512166934273844),
              (69331, 5.2023046454335375),
              (69664, 4.911275621078286),
              (69997, 4.636013525927218),
              (70330, 4.374203524527452),
              (70663, 4.124047219995475),
              (70996, 3.8841144416980384),
              (71329, 3.653245612783644),
              (71662, 3.4304850756655063),
              (71995, 3.2150341614377136),
              (72328, 3.006217295350048),
              (72661, 2.8034569681503068),
              (72994, 2.6062548935828236),
              (73327, 2.4141775799804335),
              (73660, 2.2268451142747008),
              (73993, 2.0439223252359664),
              (74326, 1.865111736705767),
              (74659, 1.690147886653708),
              (74992, 1.5187927017971425),
              (75325, 1.3508316975276191),
              (75658, 1.1860708299932108),
              (75991, 1.0243338685476875),
              (76324, 0.8654601871411315),
              (76657, 0.7093028957937032),
              (76990, 0.5557272502584478),
              (77323, 0.40460929086707503),
              (77656, 0.2558346714396311),
              (77989, 0.10929764679365304),
              (78322, 0.0),
              (78655, 0.0),
              (78988, 0.0),
              (79321, 0.0),
              (79654, 0.0),
              (79987, 0.0),
              (80320, 0.0),
              (80653, 0.0),
              (80986, 0.0),
              (81319, 0.0),
              (81652, 0.0),
              (81985, 0.0),
              (82318, 0.0),
              (82651, 0.0),
              (82984, 0.0),
              (83317, 0.0),
              (83332, 0.0),
            ]),
          },
          'ni/Dev1/ao1': {
            (-2,): ('step', [(83333, -5.0)]),
            (-1,): ('step', [(0, -5.0)]),
          },
        },
      },
      'digital' : {
        'vp': {
          'vp/Dev0/A/0': {
            (-1,): ('step', [ (0, False) ]),
            (0,): ('step', [
              (200000, True),
              (399999, False),
            ]),
            (-2,): ('step', [ (1000000, False) ]),
          },
        },
      },
      'transitions' : {
        'vp/Dev0/A/13': {'dt': 6e-07 * unit.s, 'transitions': {
          0, 83332, 67333, 68998, 70663, 72328, 73993, 75658, 77323, 78988,
          80653, 82318, 83334, 50833, 52499, 54165, 55831, 57497, 59163, 16667,
          60829, 62495, 67999, 64161, 69664, 65827, 71329, 72994, 74659, 76324,
          77989, 79654, 81319, 82984, 67000, 68665, 70330, 71995, 73660, 75325,
          76990, 78655, 80320, 81985, 83333, 50000, 51666, 67666, 53332, 69331,
          54998, 70996, 56664, 72661, 58330, 74326, 59996, 75991, 61662, 77656,
          63328, 79321, 64994, 80986, 66660, 82651, 66666, 66667, 68332, 69997,
          71662, 73327, 74992, 76657, 78322, 79987, 81652, 83317,
        }},
        'vp/Dev0/Internal_XO': {'dt': 5e-08 * unit.s, 'transitions': {
          200000, 0, 1000000, 399999,
        }},
      },
      'clocks' : { # clocks
        'vp/Dev0/A/0': ('vp/Dev0/Internal_XO', 5e-08 * unit.s),
        'ni/Dev1/ao0': ('vp/Dev0/A/13', 6e-07 * unit.s),
        'ni/Dev1/ao1': ('vp/Dev0/A/13', 6e-07 * unit.s),
      },
      't_max' : 0.05000120000000001*unit.s, # t_max
      'eval_cache' : {
        (0,): {'t': 0.01 * unit.s, 'dt': 0.01 * unit.s,
               'val': 'pulse(True, False)'},
        (1,): {'t': 0.010000199999999999 * unit.s,
               'dt': 0.009999599999999999 * unit.s,
               'val': '<2.0 kg m^2 / A s^3>'},
        (2,): {'t': 0.03 * unit.s, 'dt': 0.010000199999999999 * unit.s,
               'val': 'ramp(10.0*V, 1.0, 20, 0.0*V, None, '
                           '0.010000199999999999*s)'},
        (3,): {'t': 0.0400002 * unit.s, 'dt': 0.009999599999999999 * unit.s,
               'val': '-12.0*kilogram*meter**2*x**0.5/(ampere*second**3) + '
                      '10.0*kilogram*meter**2/(ampere*second**3)'},
      },
    },
  }

  def run_waveforms_test(self, type):
    waveforms = add_waveform_paths(
      self.L['waveforms']['waveforms'][self.L['waveforms']['current_waveform']]
    )

    analog, digital, transitions, dev_clocks, t_max, eval_cache = \
    compute.waveforms(
      self.L['devices'],
      self.L['clocks'],
      self.L['signals'],
      self.L['channels'],
      waveforms,
      self.G, continuous=(type=='continuous') )

    # has some precision problems with comparing.  so we'll compare with textual
    # versions
    self.assertEqual(analog, self.waveform_answer[type]['analog'])

    self.assertEqual(digital,     self.waveform_answer[type]['digital'])
    self.assertEqual(transitions, self.waveform_answer[type]['transitions'])
    self.assertEqual(dev_clocks,  self.waveform_answer[type]['clocks'])
    self.assertAlmostEqual(t_max/unit.s,
                           self.waveform_answer[type]['t_max']/unit.s)

    # has some precision problems with comparing.  so we'll compare with textual
    # versions
    self.assertEqual(eval_cache, self.waveform_answer[type]['eval_cache'])


  def test_continuous_waveforms(self):
    self.run_waveforms_test('continuous')

  def test_non_continuous_waveforms(self):
    self.run_waveforms_test('non-continuous')

  def runTest(self):
    """This function does nothing, but is implemented to make debugging tests
    easier"""
    pass



def add_waveform_paths( waveforms, parent_path=() ):
  waveforms = copy.deepcopy( waveforms )
  for sibling_number, wve in zip( range(len(waveforms)), waveforms ):
    current_path = parent_path + (sibling_number,)
    if 'elements' in wve:
      # recurse to elements within group
      add_waveform_paths( wve['elements'], current_path )
    else:
      wve['path'] = current_path
  return waveforms
