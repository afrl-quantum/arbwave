# vim: ts=2:sw=2:tw=80:nowrap

from timing import Timing, InternalTiming
from ....channels import Digital as DBase
from ....channels import Backplane as BBase

class Digital(DBase): pass
class Backplane(BBase): pass
