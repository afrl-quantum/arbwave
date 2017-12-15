#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
This file is not really for a normal package import
"""

from bbb_pyro import BBB_PYRO_GROUP, format_objectId

def main(klass):
  import argparse, socket

  hostname = socket.gethostname()
  parser = argparse.ArgumentParser()
  parser.add_argument('--hostid', default=hostname,
    help='Specify the hostid label for this BeagleBone Black [Default: {}]'
         .format(hostname))
  parser.add_argument('--replace', action='store_true',
    help='Replace any currently registered instances matching this '
         'hostid/deviceid with this instance.')
  parser.add_argument('--ns', metavar='NAMESERVER[:PORT]',
    help='Specify Pyro nameserver address (in case it cannot be reached by UDP '
         'broadcasts).')
  args = parser.parse_args()

  import Pyro.core, Pyro.naming
  Pyro.core.initServer()

  # locate the NS
  try:
    if args.ns:
      uri = Pyro.core.PyroURI('PYRONAME://{}/:Pyro.NameServer'.format(args.ns))
      ns = Pyro.naming.NameServerProxy(uri)
    else:
      locator = Pyro.naming.NameServerLocator()
      print 'searching for Naming Service...'
      ns = locator.getNS()

    bind_ip = ns.adapter.conn.sock.getsockname()[0]
  except Pyro.core.NamingError:
    print 'Could not find name server'
    ns = None
    bind_ip = args.hostid

  daemon = Pyro.core.Daemon(host=bind_ip)
  if ns:
    daemon.useNameServer(ns)

    # make sure our namespace group exists
    try: ns.createGroup(BBB_PYRO_GROUP)
    except Pyro.core.NamingError: pass

  obj = Pyro.core.ObjBase()
  device = klass(args.hostid)
  obj.delegateTo(device)

  if args.replace and ns and device.objectId in dict(ns.flatlist()).iterkeys():
    ns.unregister(device.objectId)

  uri = daemon.connect(obj, device.objectId)
  print 'my uri is: ', uri

  try:
    daemon.requestLoop()
  except:
    if ns:
      # try removing self from Pyro name server
      try: ns.unregister(device.objectId)
      except Pyro.core.NamingError: pass
