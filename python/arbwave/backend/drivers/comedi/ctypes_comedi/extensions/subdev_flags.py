# vim: ts=2:sw=2:tw=80:nowrap

from .. import ctypes_comedi as comedi

def to_dict( flags ):
  class Dict(dict):
    def __init__(self, *a, **kw):
      super(Dict,self).__init__(*a, **kw)
      self.__dict__ = self

  D = Dict(
    busy                  =     bool(flags & comedi.SDF_BUSY),
    busy_owner            =     bool(flags & comedi.SDF_BUSY_OWNER),
    locked                =     bool(flags & comedi.SDF_LOCKED),
    lock_owner            =     bool(flags & comedi.SDF_LOCK_OWNER),
    maxdata_per_channel   =     bool(flags & comedi.SDF_MAXDATA),
    flags_per_channel     =     bool(flags & comedi.SDF_FLAGS),
    rangetype_per_channel =     bool(flags & comedi.SDF_RANGETYPE),
    async_cmd_supported   =     bool(flags & comedi.SDF_CMD),
    soft_calibrated       =     bool(flags & comedi.SDF_SOFT_CALIBRATED),
    readable              =     bool(flags & comedi.SDF_READABLE),
    writeable             =     bool(flags & comedi.SDF_WRITEABLE),
    internal              =     bool(flags & comedi.SDF_INTERNAL),
    aref_ground_supported =     bool(flags & comedi.SDF_GROUND),
    aref_common_supported =     bool(flags & comedi.SDF_COMMON),
    aref_diff_supported   =     bool(flags & comedi.SDF_DIFF),
    aref_other_supported  =     bool(flags & comedi.SDF_OTHER),
    dither_supported      =     bool(flags & comedi.SDF_DITHER),
    deglitch_supported    =     bool(flags & comedi.SDF_DEGLITCH),
    running               =     bool(flags & comedi.SDF_RUNNING),
    sample_32bit          =     bool(flags & comedi.SDF_LSAMPL),
    sample_16bit          = not bool(flags & comedi.SDF_LSAMPL),
    sample_bitwise        =     bool(flags & comedi.SDF_PACKED),
  )
  return D

#comedi.subdev_flags_to_dict = to_dict
