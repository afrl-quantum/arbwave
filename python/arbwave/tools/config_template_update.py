# vim: ts=2:sw=2:tw=80:nowrap

def recursive_update(D, new):
  """
  Recursively update the config template hierarchy.  The intent of this function
  is to allow configuration items to be added to a device config without
  requiring an file-version upgrade.  This is only possible, if the new items
  come with reasonable defaults.
  if
    - a configuration item must be changed
    - a configuration item must be removed
    - a new configuration item does not come with reasonable defaults
  then a new file-version upgrade _must_ be implemented.
  """
  for k, dsub in new.iteritems():
    if 'value' in dsub:
      D[k] = dsub.copy()
    else:
      recursive_update(D.setdefault(k, dict()), dsub)


