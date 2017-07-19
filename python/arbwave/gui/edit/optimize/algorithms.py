# vim: ts=2:sw=2:tw=80:nowrap
"""
Definitions of all optimization algorithms provided by Arbwave.

Each algorithm is assigned a unique name (such as 'Powell').  The function
that performs the optimization is also specified as the 'func' entry.  The
signature of this function should be:
  func( merit_function, x0, **kwargs)

  where the signature of the merit function is always:
  merit_function(x0)
    ...do stuff...
    return merit_value

  x0 represents the current optimization parameter space vector (initial
  parameters are passed into the algorithm and then passed to the merit function
  by the algorithm as they are modified), and kwargs are all the parameters
  specified by the user and defined also in the 'parameters' entry for each
  algorithm.

  An example set of parameters are specifed as:
    'parameters' : {
      'args'      : {'order':0, 'enable':False,'type':str,  'value':'()',  'range':None},
      'xtol'      : {'order':1, 'enable':True, 'type':float,'value':0.0001,'range':[0,FMAX,1e-4,1e-3],   'combo':False},
      'ftol'      : {'order':2, 'enable':True, 'type':float,'value':0.0001,'range':[0,FMAX,1e-4,1e-3],   'combo':False},
      'maxiter'   : {'order':3, 'enable':False,'type':int,  'value':4000,  'range':xrange(sys.maxint)},
      'maxfun'    : {'order':4, 'enable':False,'type':int,  'value':4000,  'range':xrange(sys.maxint)},
      'disp'      : {'order':5, 'enable':True, 'type':bool, 'value':True,  'range':None},
      #'retall'   : {'order':6, 'enable':False,'type':bool, 'value':False,'range':None},
      'callback'  : {'order':7, 'enable':False,'type':str,  'value':'',    'range':None},
      'direc'     : {'order':8, 'enable':False,'type':str,  'value':'',    'range':None},
    },

  Documentation for the algorithm
"""

import sys

from scipy import optimize as opt

FMAX = sys.float_info.max
inf  = float('inf')

algorithms = {
  'Powell'              : {
    'func' : lambda *a, **kw: opt.fmin_powell(full_output=True,*a,**kw)[0:2],
    'actual_func' : opt.fmin_powell,
    'enable' : False,
    'order'  : 1,
    'parameters' : {
      'args'      : {'order':0, 'enable':False,'type':str,  'value':'()',  'range':None},
      'xtol'      : {'order':1, 'enable':True, 'type':float,'value':0.0001,'range':[0,FMAX,1e-4,1e-3],   'combo':False},
      'ftol'      : {'order':2, 'enable':True, 'type':float,'value':0.0001,'range':[0,FMAX,1e-4,1e-3],   'combo':False},
      'maxiter'   : {'order':3, 'enable':False,'type':int,  'value':4000,  'range':xrange(sys.maxint)},
      'maxfun'    : {'order':4, 'enable':False,'type':int,  'value':4000,  'range':xrange(sys.maxint)},
      'disp'      : {'order':5, 'enable':True, 'type':bool, 'value':True,  'range':None},
      #'retall'   : {'order':6, 'enable':False,'type':bool, 'value':False,'range':None},
      'callback'  : {'order':7, 'enable':False,'type':str,  'value':'',    'range':None},
      'direc'     : {'order':8, 'enable':False,'type':str,  'value':'',    'range':None},
    },
  },
  'Simplex'             : {
    'func' : lambda *a, **kw: opt.fmin(full_output=True,*a,**kw)[0:2],
    'actual_func' : opt.fmin,
    'enable' : False,
    'order'  : 2,
    'parameters' : {
      'args'      : {'order':0, 'enable':False,'type':str,  'value':'()',  'range':None},
      'xtol'      : {'order':1, 'enable':True, 'type':float,'value':0.0001,'range':[0,FMAX,1e-4,1e-3],   'combo':False},
      'ftol'      : {'order':2, 'enable':True, 'type':float,'value':0.0001,'range':[0,FMAX,1e-4,1e-3],   'combo':False},
      'maxiter'   : {'order':3, 'enable':False,'type':int,  'value':4000,  'range':xrange(sys.maxint)},
      'maxfun'    : {'order':4, 'enable':False,'type':int,  'value':4000,  'range':xrange(sys.maxint)},
      'disp'      : {'order':5, 'enable':True, 'type':bool, 'value':True,  'range':None},
      #'retall'   : {'order':6, 'enable':False,'type':bool, 'value':False,'range':None},
      'callback'  : {'order':7, 'enable':False,'type':str,  'value':'',    'range':None},
    },
  },
  'BFGS'                : {
    'func' : lambda *a, **kw: opt.fmin_bfgs(full_output=True,*a,**kw)[0:2],
    'actual_func' : opt.fmin_bfgs,
    'enable' : False,
    'order'  : 3,
    'parameters' : {
      'fprime'    : {'order':0,'enable':False,'type':str,  'value':'',    'range':None},
      'args'      : {'order':1,'enable':False,'type':str,  'value':'()',  'range':None},
      'gtol'      : {'order':2,'enable':True, 'type':float,'value':1e-05, 'range':[0,FMAX,1e-5,1e-4],   'combo':False},
      'norm'      : {'order':3,'enable':True, 'type':float,'value':inf,   'range':[0,FMAX,1,10],        'combo':False},
      'epsilon'   : {'order':4,'enable':True, 'type':float,'value':1.5e-08,'range':[0,FMAX,0.5e-8,1e-7],'combo':False},
      'maxiter'   : {'order':5,'enable':False,'type':int,  'value':4000,  'range':xrange(sys.maxint)},
      'disp'      : {'order':6,'enable':True, 'type':bool, 'value':True,  'range':None},
      #'retall'   : {'order':7,'enable':False,'type':bool, 'value':False,'range':None},
      'callback'  : {'order':8,'enable':False,'type':str,  'value':'',    'range':None},
    },
  },
  'L-BFGS-B'            : {
    'func' : lambda *a,**kw: opt.fmin_l_bfgs_b(*a,**kw)[0:2],
    'actual_func' : opt.fmin_l_bfgs_b,
    'enable' : False,
    'order'  : 4,
    'parameters' : {
      'fprime'      : {'order':0, 'enable':False,'type':str,  'value':'',    'range':None},
      'args'        : {'order':1, 'enable':False,'type':str,  'value':'()',  'range':None},
      'approx_grad' : {'order':2, 'enable':True, 'type':bool, 'value':True,  'range':None},
      'bounds'      : {'order':3, 'enable':False,'type':str,  'value':'',    'range':None},
      'm'           : {'order':4, 'enable':True, 'type':int,  'value':10,    'range':xrange(sys.maxint)},
      'factr'       : {'order':5, 'enable':True, 'type':float,'value':1e7,   'range':[0,FMAX,1e6,1e7],  'combo':False},
      'pgtol'       : {'order':6, 'enable':True, 'type':float,'value':1e-5,  'range':[0,FMAX,1e-5,1e-4],'combo':False},
      'epsilon'     : {'order':7, 'enable':True, 'type':float,'value':1e-8,  'range':[0,FMAX,1e-8,1e-7],'combo':False},
      'iprint'      : {'order':8, 'enable':True, 'type':int,  'value':-1,    'range':xrange(-1,sys.maxint-1)},
      'maxfun'      : {'order':9, 'enable':False,'type':int,  'value':15000, 'range':xrange(sys.maxint)},
      'disp'        : {'order':10,'enable':False,'type':bool, 'value':True,  'range':None},
    },
  },
}

if hasattr(opt,'anneal'):
  # this one did not show up on some windows versions for some reason...
  algorithms['Simulated Annealing'] = {
    'func' : lambda *a,**kw: opt.anneal(full_output=True, *a, **kw)[0:2],
    'actual_func' : opt.anneal,
    'enable' : False,
    'order'  : 0,
    'parameters' : {
      'args'      : {'order':0, 'enable':False,'type':str,  'value':'()',  'range':None},
      'schedule'  : {'order':1, 'enable':True, 'type':str,  'value':'fast','range':['fast','cauchy','boltzmann']},
      'T0'        : {'order':2, 'enable':False,'type':float,'value':1,     'range':[0,FMAX,1,1],         'combo':False},
      'Tf'        : {'order':3, 'enable':True, 'type':float,'value':1e-12, 'range':[0,FMAX,1e-12,1e-10], 'combo':False},
      'maxeval'   : {'order':4, 'enable':False,'type':int,  'value':4000,  'range':[0,sys.maxint,10,100],'combo':False},
      'maxaccept' : {'order':5, 'enable':False,'type':int,  'value':4000,  'range':[0,sys.maxint,10,100],'combo':False},
      'maxiter'   : {'order':6, 'enable':True, 'type':int,  'value':400,   'range':[0,sys.maxint,10,100],'combo':False},
      'boltzmann' : {'order':7, 'enable':True, 'type':float,'value':1.0,   'range':[0,FMAX,.1,1],        'combo':False},
      'learn_rate': {'order':8, 'enable':True, 'type':float,'value':0.5,   'range':[0,FMAX,.1,1],        'combo':False},
      'feps'      : {'order':9, 'enable':True, 'type':float,'value':1e-6,  'range':[0,FMAX,1e-6,1e-5],   'combo':False},
      'quench'    : {'order':10,'enable':True, 'type':float,'value':1.0,   'range':[0,FMAX,.1,1],        'combo':False},
      'm'         : {'order':11,'enable':True, 'type':float,'value':1.0,   'range':[0,FMAX,.1,1],        'combo':False},
      'n'         : {'order':12,'enable':True, 'type':float,'value':1.0,   'range':[0,FMAX,.1,1],        'combo':False},
      'lower'     : {'order':13,'enable':False,'type':float,'value':-100,  'range':[-FMAX,FMAX,1,1],     'combo':False},
      'upper'     : {'order':14,'enable':False,'type':float,'value':100,   'range':[-FMAX,FMAX,1,1],     'combo':False},
      'dwell'     : {'order':15,'enable':True, 'type':int,  'value':50,    'range':[0,sys.maxint,1,10],  'combo':False},
    },
  }

def safe_repr(x):
  if x in [ inf, -inf ]:
    return "float('{inf}')".format(inf=repr(x))
  return repr(x)
