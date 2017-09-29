#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
This file is not really for a normal package import
"""

import sys
from os.path import join as path_join, dirname, pardir
sys.path.insert(0, path_join( dirname(__file__), *((pardir,)*5) ) )


def main(klass):
  import argparse, socket

  hostname = socket.gethostname()
  parser = argparse.ArgumentParser()
  parser.add_argument('--hostid', default=hostname,
    help='Specify the hostid label for this BeagleBone Black [Default: {}]'
         .format(hostname))
  args = parser.parse_args()

  import Pyro.core, Pyro.naming
  Pyro.core.initServer()

  # locate the NS
  daemon = Pyro.core.Daemon()
  try:
    locator = Pyro.naming.NameServerLocator()
    print 'searching for Naming Service...'
    ns = locator.getNS()
  except NamingError:
    ns = None

  if ns is not None:
    print 'Could not find name server'
    daemon.useNameServer(ns)

    # make sure our namespace group exists
    try: ns.createGroup(BBB_PYRO_GROUP)
    except NamingError: pass

  obj = Pyro.core.ObjBase()
  device = klass(args.hostid)
  obj.delegateTo(device)
  uri = daemon.connect(obj, device.objectId)
  print 'my uri is: ', uri

  try:
    daemon.requestLoop()
  except:
    # try removing self from Pyro name server
    try: ns.unregister(device.objectId)
    except NamingError: pass
