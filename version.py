# vim: ts=2:sw=2:tw=80:nowrap

from subprocess import Popen, PIPE

def git_version():
  try:
    p = Popen(['git', 'describe'], stdout=PIPE)
    out,err = p.communicate()
    return out.strip()
  except:
    return 'arbwave-UNKNOWN'

def version():
  gv = git_version()
  return gv[ (gv.find('-')+1):]

def prefix():
  return git_version().split('-')[0]

