# vim: ts=2:sw=2:tw=80:nowrap


from .base import Base
from .timing      import *
from ....channels import Analog as ABase
from ....channels import Digital as DBase
from ....channels import Backplane as BBase

class Analog(Base, ABase): pass
class Digital(Base, DBase): pass
class Backplane(BBase): pass


klasses = dict(
  to = Timing,
  ao = Analog,
  do = Digital,
  backplane = Backplane,
)
