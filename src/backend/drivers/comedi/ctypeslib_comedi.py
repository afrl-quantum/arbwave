from ctypes import *

_libraries = {}
_libraries['libcomedi.so.0'] = CDLL('libcomedi.so.0')
STRING = c_char_p


F_OWNER_PGRP = 2
COMEDI_SUPPORTED = 1
F_OWNER_TID = 0
INSN_CONFIG_BLOCK_SIZE = 22
COMEDI_COUNTER_TERMINAL_COUNT = 4
COMEDI_COUNTER_COUNTING = 2
# __BLKCNT64_T_TYPE = __SQUAD_TYPE # alias
F_OWNER_GID = 2
__S_IFCHR = 8192 # Variable c_int '8192'
S_IFCHR = __S_IFCHR # alias
F_OWNER_PID = 1
COMEDI_UNKNOWN_SUPPORT = 0
NI_GPCT_SOURCE_ENCODER_Z = 2
# _IO_HAVE_ST_BLKSIZE = _G_HAVE_ST_BLKSIZE # alias
NI_GPCT_INDEX_PHASE_MASK = 3145728
NI_GPCT_SOURCE_ENCODER_B = 1
NI_GPCT_COUNTING_MODE_SYNC_SOURCE_BITS = 393216
NI_GPCT_SOURCE_ENCODER_A = 0
INSN_CONFIG_PWM_GET_H_BRIDGE = 5004
INSN_CONFIG_PWM_GET_PERIOD = 5001
INSN_CONFIG_PWM_SET_PERIOD = 5000
INSN_CONFIG_GET_ROUTING = 4109
INSN_CONFIG_SET_ROUTING = 4099
INSN_CONFIG_8254_READ_STATUS = 4098
INSN_CONFIG_8254_SET_MODE = 4097
INSN_CONFIG_GET_HARDWARE_BUFFER_SIZE = 2006
INSN_CONFIG_SET_OTHER_SRC = 2005
INSN_CONFIG_GET_GATE_SRC = 2002
INSN_CONFIG_GPCT_QUADRATURE_ENCODER = 1003
INSN_CONFIG_GPCT_SINGLE_PULSE_GENERATOR = 1001
INSN_CONFIG_RESET = 34
INSN_CONFIG_DISARM = 32
INSN_CONFIG_ARM = 31
INSN_CONFIG_PWM_OUTPUT = 29
INSN_CONFIG_DIO_QUERY = 28
INSN_CONFIG_BIDIRECTIONAL_DATA = 27
INSN_CONFIG_SERIAL_CLOCK = 26
INSN_CONFIG_CHANGE_NOTIFY = 25
INSN_CONFIG_FILTER = 24
INSN_CONFIG_TIMER_1 = 23
SDF_MODE0 = 128 # Variable c_int '128'
SDF_PWM_COUNTER = SDF_MODE0 # alias
COMEDI_COUNTER_ARMED = 1
def putc(_ch,_fp): return _IO_putc (_ch, _fp) # macro
def minor(dev): return gnu_dev_minor (dev) # macro
def makedev(maj,min): return gnu_dev_makedev (maj, min) # macro
def major(dev): return gnu_dev_major (dev) # macro
def le64toh(x): return (x) # macro
def le32toh(x): return (x) # macro
AMPLC_DIO_CLK_1KHZ = 5
NI_GPCT_COUNTING_MODE_QUADRATURE_X1_BITS = 65536
NI_GPCT_SOURCE_PIN_i_CLOCK_SRC_BITS = 6
NI_GPCT_NEXT_GATE_CLOCK_SRC_BITS = 4
NI_GPCT_TIMEBASE_2_CLOCK_SRC_BITS = 1
NI_GPCT_CLOCK_SRC_SELECT_MASK = 63
# __FSBLKCNT64_T_TYPE = __UQUAD_TYPE # alias
# __S32_TYPE = int # alias
# __CLOCKID_T_TYPE = __S32_TYPE # alias
I8254_MODE4 = 8
I8254_MODE3 = 6
NI_PFI_FILTER_2550us = 3
NI_GPCT_PXI_STAR_TRIGGER_CLOCK_SRC_BITS = 8
NI_GPCT_NEXT_TC_CLOCK_SRC_BITS = 5
def _IOR_BAD(type,nr,size): return _IOC(_IOC_READ,(type),(nr),sizeof(size)) # macro
NI_GPCT_LOGIC_LOW_CLOCK_SRC_BITS = 3
NI_GPCT_TIMEBASE_3_CLOCK_SRC_BITS = 2
# def __bswap_16(x): return (__extension__ ({ unsigned short int __v, __x = (unsigned short int) (x); if (__builtin_constant_p (__x)) __v = __bswap_constant_16 (__x); else __asm__ ("rorw $8, %w0" : "=r" (__v) : "0" (__x) : "cc"); __v; })) # macro
def __bos0(ptr): return __builtin_object_size (ptr, 0) # macro
# _IO_wint_t = wint_t # alias
def __bos(ptr): return __builtin_object_size (ptr, __USE_FORTIFY_LEVEL > 1) # macro
# __INO64_T_TYPE = __UQUAD_TYPE # alias
def __attribute_format_strfmon__(a,b): return __attribute__ ((__format__ (__strfmon__, a, b))) # macro
__ssize_t = c_long
_IO_ssize_t = __ssize_t # alias
size_t = c_ulong
_IO_size_t = size_t # alias
NI_PFI_FILTER_125ns = 1
__off_t = c_long
_IO_off_t = __off_t # alias
__off64_t = c_long
_IO_off64_t = __off64_t # alias
COMEDI_UNSUPPORTED = 2
# def __S_TYPEISSEM(buf): return ((buf)->st_mode - (buf)->st_mode) # macro
# _IO_iconv_t = _G_iconv_t # alias
# def __S_TYPEISMQ(buf): return ((buf)->st_mode - (buf)->st_mode) # macro
class _G_fpos64_t(Structure):
    pass
class __mbstate_t(Structure):
    pass
class N11__mbstate_t4DOT_14E(Union):
    pass
N11__mbstate_t4DOT_14E._fields_ = [
    ('__wch', c_uint),
    ('__wchb', c_char * 4),
]
__mbstate_t._fields_ = [
    ('__count', c_int),
    ('__value', N11__mbstate_t4DOT_14E),
]
_G_fpos64_t._fields_ = [
    ('__pos', __off64_t),
    ('__state', __mbstate_t),
]
_IO_fpos64_t = _G_fpos64_t # alias
_G_BUFSIZ = 8192 # Variable c_int '8192'
_IO_BUFSIZ = _G_BUFSIZ # alias
NI_PFI_FILTER_OFF = 0
# def __REDIRECT(name,proto,alias): return name proto __asm__ (__ASMNAME (#alias)) # macro
CMDF_PRIORITY = 8 # Variable c_int '8'
TRIG_RT = CMDF_PRIORITY # alias
TIOCM_RNG = 128 # Variable c_int '128'
TIOCM_RI = TIOCM_RNG # alias
def __PMT(args): return args # macro
# def __NTH(fct): return __LEAF_ATTR fct throw () # macro
__S_IEXEC = 64 # Variable c_int '64'
S_IXUSR = __S_IEXEC # alias
__S_ISVTX = 512 # Variable c_int '512'
S_ISVTX = __S_ISVTX # alias
__S_ISUID = 2048 # Variable c_int '2048'
S_ISUID = __S_ISUID # alias
# def __LDBL_REDIR1(name,proto,alias): return name proto # macro
__S_IFREG = 32768 # Variable c_int '32768'
S_IFREG = __S_IFREG # alias
__S_IFMT = 61440 # Variable c_int '61440'
S_IFMT = __S_IFMT # alias
__codecvt_noconv = 3
__codecvt_error = 2
__codecvt_partial = 1
__codecvt_ok = 0
# def __FD_ZERO(fdsp): return do { int __d0, __d1; __asm__ __volatile__ ("cld; rep; " __FD_ZERO_STOS : "=c" (__d0), "=D" (__d1) : "a" (0), "0" (sizeof (fd_set) / sizeof (__fd_mask)), "1" (&__FDS_BITS (fdsp)[0]) : "memory"); } while (0) # macro
class _IO_FILE(Structure):
    pass
stdout = (POINTER(_IO_FILE)).in_dll(_libraries['libcomedi.so.0'], 'stdout')
stdout = stdout # alias
__S_IFDIR = 16384 # Variable c_int '16384'
S_IFDIR = __S_IFDIR # alias
def __FD_ISSET(d,set): return ((__FDS_BITS (set)[__FD_ELT (d)] & __FD_MASK (d)) != 0) # macro
stderr = (POINTER(_IO_FILE)).in_dll(_libraries['libcomedi.so.0'], 'stderr')
stderr = stderr # alias
# __wur = __attribute_warn_unused_result__ # alias
# def __FD_CLR(d,set): return ((void) (__FDS_BITS (set)[__FD_ELT (d)] &= ~__FD_MASK (d))) # macro
NI_GPCT_DISABLED_OTHER_SELECT = 32768
# __USECONDS_T_TYPE = __U32_TYPE # alias
# def __FDS_BITS(set): return ((set)->fds_bits) # macro
SDF_WRITABLE = 131072 # Variable c_int '131072'
SDF_WRITEABLE = SDF_WRITABLE # alias
# __UID_T_TYPE = __U32_TYPE # alias
def __CONCAT(x,y): return x ## y # macro
# __FSFILCNT64_T_TYPE = __UQUAD_TYPE # alias
SDF_MODE1 = 256 # Variable c_int '256'
SDF_PWM_HBRIDGE = SDF_MODE1 # alias
NI_PFI_OUTPUT_RTSI0 = 18
NI_GPCT_ARM_UNKNOWN = 4096
NI_GPCT_ARM_PAIRED_IMMEDIATE = 1
NI_GPCT_ARM_IMMEDIATE = 0
def CR_PACK(chan,rng,aref): return ( (((aref)&0x3)<<24) | (((rng)&0xff)<<16) | (chan) ) # macro
# __SYSCALL_ULONG_TYPE = __ULONGWORD_TYPE # alias
INSN_CONFIG_DIGITAL_TRIG = 21
INSN_CONFIG_ALT_SOURCE = 20
INSN_CONFIG_ANALOG_TRIG = 16
INSN_CONFIG_DIO_OPENDRAIN = 2
INSN_CONFIG_DIO_OUTPUT = 1
INSN_CONFIG_DIO_INPUT = 0
NI_PFI_OUTPUT_GOUT1 = 14
# __SYSCALL_SLONG_TYPE = __SLONGWORD_TYPE # alias
# __SUSECONDS_T_TYPE = __SYSCALL_SLONG_TYPE # alias
# __SSIZE_T_TYPE = __SWORD_TYPE # alias
COMEDI_FROM_PHYSICAL = 1
COMEDI_TO_PHYSICAL = 0
NI_PFI_OUTPUT_G_SRC0 = 9
# def _IO_feof_unlocked(__fp): return (((__fp)->_flags & _IO_EOF_SEEN) != 0) # macro
NI_PFI_OUTPUT_AO_START1 = 7
# __RLIM64_T_TYPE = __UQUAD_TYPE # alias
NI_PFI_OUTPUT_G_SRC1 = 4
# __OFF_T_TYPE = __SYSCALL_SLONG_TYPE # alias
def _IOWR_BAD(type,nr,size): return _IOC(_IOC_READ|_IOC_WRITE,(type),(nr),sizeof(size)) # macro
def le16toh(x): return (x) # macro
def _IOWR(type,nr,size): return _IOC(_IOC_READ|_IOC_WRITE,(type),(nr),(_IOC_TYPECHECK(size))) # macro
def htole32(x): return (x) # macro
def htole16(x): return (x) # macro
def htobe64(x): return __bswap_64 (x) # macro
def htobe32(x): return __bswap_32 (x) # macro
# __OFF64_T_TYPE = __SQUAD_TYPE # alias
def htobe16(x): return __bswap_16 (x) # macro
def getc(_fp): return _IO_getc (_fp) # macro
def _IOW(type,nr,size): return _IOC(_IOC_WRITE,(type),(nr),(_IOC_TYPECHECK(size))) # macro
def be64toh(x): return __bswap_64 (x) # macro
def be32toh(x): return __bswap_32 (x) # macro
def be16toh(x): return __bswap_16 (x) # macro
# def __warndecl(name,msg): return extern void name (void) __attribute__((__warning__ (msg))) # macro
# __NLINK_T_TYPE = __SYSCALL_ULONG_TYPE # alias
def __warnattr(msg): return __attribute__((__warning__ (msg))) # macro
def __va_arg_pack_len(): return __builtin_va_arg_pack_len () # macro
def __va_arg_pack(): return __builtin_va_arg_pack () # macro
# def __u_intN_t(N,MODE): return typedef unsigned int u_int ##N ##_t __attribute__ ((__mode__ (MODE))) # macro
# def __nonnull(params): return __attribute__ ((__nonnull__ params)) # macro
# def __intN_t(N,MODE): return typedef int int ##N ##_t __attribute__ ((__mode__ (MODE))) # macro
def __glibc_unlikely(cond): return __builtin_expect ((cond), 0) # macro
def _IOR(type,nr,size): return _IOC(_IOC_READ,(type),(nr),(_IOC_TYPECHECK(size))) # macro
def __glibc_likely(cond): return __builtin_expect ((cond), 1) # macro
# def __errordecl(name,msg): return extern void name (void) __attribute__((__error__ (msg))) # macro
# def __bswap_constant_64(x): return (__extension__ ((((x) & 0xff00000000000000ull) >> 56) | (((x) & 0x00ff000000000000ull) >> 40) | (((x) & 0x0000ff0000000000ull) >> 24) | (((x) & 0x000000ff00000000ull) >> 8) | (((x) & 0x00000000ff000000ull) << 8) | (((x) & 0x0000000000ff0000ull) << 24) | (((x) & 0x000000000000ff00ull) << 40) | (((x) & 0x00000000000000ffull) << 56))) # macro
def __bswap_constant_32(x): return ((((x) & 0xff000000) >> 24) | (((x) & 0x00ff0000) >> 8) | (((x) & 0x0000ff00) << 8) | (((x) & 0x000000ff) << 24)) # macro
# __MODE_T_TYPE = __U32_TYPE # alias
# def __bswap_constant_16(x): return ((unsigned short int) ((((x) >> 8) & 0xff) | (((x) & 0xff) << 8))) # macro
def __attribute_format_arg__(x): return __attribute__ ((__format_arg__ (x))) # macro
# def __attribute_alloc_size__(params): return __attribute__ ((__alloc_size__ params)) # macro
# def __S_TYPEISSHM(buf): return ((buf)->st_mode - (buf)->st_mode) # macro
NI_GPCT_INDEX_PHASE_HIGH_A_HIGH_B_BITS = 3145728
def __STRING(x): return #x # macro
def __REDIRECT_NTH_LDBL(name,proto,alias): return __REDIRECT_NTH (name, proto, alias) # macro
NI_PFI_FILTER_6425ns = 2
# def __REDIRECT_NTHNL(name,proto,alias): return name proto __THROWNL __asm__ (__ASMNAME (#alias)) # macro
# def __REDIRECT_NTH(name,proto,alias): return name proto __THROW __asm__ (__ASMNAME (#alias)) # macro
def __REDIRECT_LDBL(name,proto,alias): return __REDIRECT (name, proto, alias) # macro
def __RANGE(a,b): return ((((a)&0xffff)<<16)|((b)&0xffff)) # macro
def _IOC_NR(nr): return (((nr) >> _IOC_NRSHIFT) & _IOC_NRMASK) # macro
def __P(args): return args # macro
def __LONG_LONG_PAIR(HI,LO): return LO, HI # macro
# def __LDBL_REDIR_NTH(name,proto): return name proto __THROW # macro
def _IOC_DIR(nr): return (((nr) >> _IOC_DIRSHIFT) & _IOC_DIRMASK) # macro
# def __LDBL_REDIR1_NTH(name,proto,alias): return name proto __THROW # macro
# def __LDBL_REDIR(name,proto): return name proto # macro
def __GLIBC_PREREQ(maj,min): return ((__GLIBC__ << 16) + __GLIBC_MINOR__ >= ((maj) << 16) + (min)) # macro
def _IOC(dir,type,nr,size): return (((dir) << _IOC_DIRSHIFT) | ((type) << _IOC_TYPESHIFT) | ((nr) << _IOC_NRSHIFT) | ((size) << _IOC_SIZESHIFT)) # macro
# def __FD_SET(d,set): return ((void) (__FDS_BITS (set)[__FD_ELT (d)] |= __FD_MASK (d))) # macro
# def __FD_MASK(d): return ((__fd_mask) 1 << ((d) % __NFDBITS)) # macro
# def __ASMNAME2(prefix,cname): return __STRING (prefix) cname # macro
def __ASMNAME(cname): return __ASMNAME2 (__USER_LABEL_PREFIX__, cname) # macro
# def _IO_putc_unlocked(_ch,_fp): return (_IO_BE ((_fp)->_IO_write_ptr >= (_fp)->_IO_write_end, 0) ? __overflow (_fp, (unsigned char) (_ch)) : (unsigned char) (*(_fp)->_IO_write_ptr++ = (_ch))) # macro
# def _IO_peekc_unlocked(_fp): return (_IO_BE ((_fp)->_IO_read_ptr >= (_fp)->_IO_read_end, 0) && __underflow (_fp) == EOF ? EOF : *(unsigned char *) (_fp)->_IO_read_ptr) # macro
def _IO_peekc(_fp): return _IO_peekc_unlocked (_fp) # macro
# def _IO_getc_unlocked(_fp): return (_IO_BE ((_fp)->_IO_read_ptr >= (_fp)->_IO_read_end, 0) ? __uflow (_fp) : *(unsigned char *) (_fp)->_IO_read_ptr++) # macro
# def _IO_ferror_unlocked(__fp): return (((__fp)->_flags & _IO_ERR_SEEN) != 0) # macro
# def _IO_PENDING_OUTPUT_COUNT(_fp): return ((_fp)->_IO_write_ptr - (_fp)->_IO_write_base) # macro
def _IO_BE(expr,res): return __builtin_expect ((expr), res) # macro
def _IOW_BAD(type,nr,size): return _IOC(_IOC_WRITE,(type),(nr),sizeof(size)) # macro
def _IOC_TYPECHECK(t): return (sizeof(t)) # macro
def _IOC_TYPE(nr): return (((nr) >> _IOC_TYPESHIFT) & _IOC_TYPEMASK) # macro
def _IOC_SIZE(nr): return (((nr) >> _IOC_SIZESHIFT) & _IOC_SIZEMASK) # macro
def _IO(type,nr): return _IOC(_IOC_NONE,(type),(nr),0) # macro
def SWIG_OUTPUT(x): return x # macro
def SWIG_INPUT(x): return x # macro
def SWIG_INOUT(x): return x # macro
def RF_UNIT(flags): return ((flags)&0xff) # macro
def RANGE_OFFSET(a): return (((a)>>16)&0xffff) # macro
def RANGE_LENGTH(b): return ((b)&0xffff) # macro
def FD_SET(fd,fdsetp): return __FD_SET (fd, fdsetp) # macro
def FD_ISSET(fd,fdsetp): return __FD_ISSET (fd, fdsetp) # macro
def FD_CLR(fd,fdsetp): return __FD_CLR (fd, fdsetp) # macro
def FD_ZERO(fdsetp): return __FD_ZERO (fdsetp) # macro
# __CLOCK_T_TYPE = __SYSCALL_SLONG_TYPE # alias
NI_GPCT_ANALOG_TRIGGER_OUT_CLOCK_SRC_BITS = 9
NI_GPCT_UP_DOWN_PIN_i_GATE_SELECT = 513
NI_GPCT_SOURCE_PIN_i_GATE_SELECT = 256
NI_GPCT_LOGIC_LOW_GATE_SELECT = 31
NI_GPCT_ANALOG_TRIGGER_OUT_GATE_SELECT = 30
NI_GPCT_NEXT_SOURCE_GATE_SELECT = 29
NI_GPCT_AI_START1_GATE_SELECT = 28
NI_GPCT_NEXT_OUT_GATE_SELECT = 20
NI_GPCT_PXI_STAR_TRIGGER_GATE_SELECT = 19
NI_GPCT_TIMESTAMP_MUX_GATE_SELECT = 0
def CR_RANGE(a): return (((a)>>16)&0xff) # macro
def CR_CHAN(a): return ((a)&0xffff) # macro
def CR_AREF(a): return (((a)>>24)&0x03) # macro
def COMEDI_VERSION_CODE(a,b,c): return (((a)<<16) | ((b)<<8) | (c)) # macro
# def COMEDILIB_CHECK_VERSION(major,minor,micro): return (COMEDILIB_VERSION_MAJOR > (major) || (COMEDILIB_VERSION_MAJOR == (major) && (COMEDLIB_VERSION_MINOR > (minor) || (COMEDILIB_VERSION_MINOR == (minor) && COMEDILIB_VERSION_MICRO >= (micro))))) # macro
NI_GPCT_INDEX_PHASE_HIGH_A_LOW_B_BITS = 2097152
NI_RTSI_OUTPUT_RTSI_BRD_0 = 8
NI_RTSI_OUTPUT_DA_START1 = 4
def htole64(x): return (x) # macro
INSN_CONFIG_PWM_SET_H_BRIDGE = 5003
INSN_CONFIG_GET_PWM_STATUS = 5002
AMPLC_DIO_CLK_EXT = 7
AMPLC_DIO_CLK_OUTNM1 = 6
INSN_CONFIG_GET_CLOCK_SRC = 2004
INSN_CONFIG_SET_CLOCK_SRC = 2003
INSN_CONFIG_SET_GATE_SRC = 2001
def CTRL(x): return (x&037) # macro
INSN_CONFIG_GPCT_PULSE_TRAIN_GENERATOR = 1002
NI_RTSI_OUTPUT_RTSI_OSC = 12
COMEDI_SUBD_PWM = 12
COMEDI_SUBD_SERIAL = 11
COMEDI_SUBD_PROC = 10
COMEDI_SUBD_CALIB = 9
COMEDI_SUBD_MEMORY = 8
COMEDI_SUBD_TIMER = 7
COMEDI_SUBD_COUNTER = 6
COMEDI_SUBD_DIO = 5
COMEDI_SUBD_DO = 4
COMEDI_SUBD_DI = 3
COMEDI_SUBD_AO = 2
COMEDI_SUBD_AI = 1
COMEDI_SUBD_UNUSED = 0
INSN_CONFIG_GET_COUNTER_STATUS = 33
NI_GPCT_INVERT_OUTPUT_BIT = 536870912
NI_GPCT_DISABLED_GATE_SELECT = 32768
NI_GPCT_PXI10_CLOCK_SRC_BITS = 7
NI_GPCT_SELECTED_GATE_GATE_SELECT = 542
NI_GPCT_RELOAD_SOURCE_GATE_SELECT_BITS = 134217728
NI_GPCT_RELOAD_SOURCE_SWITCHING_BITS = 67108864
NI_GPCT_GATE_PIN_i_GATE_SELECT = 257
NI_PFI_OUTPUT_CDO_UPDATE = 30
NI_GPCT_COUNTING_DIRECTION_HW_GATE_BITS = 50331648
stdin = (POINTER(_IO_FILE)).in_dll(_libraries['libcomedi.so.0'], 'stdin')
stdin = stdin # alias
NI_PFI_OUTPUT_CDI_SAMPLE = 29
NI_PFI_OUTPUT_DIO_CHANGE_DETECT_RTSI = 28
NI_PFI_OUTPUT_SCXI_TRIG1 = 27
NI_PFI_OUTPUT_PXI_STAR_TRIGGER_IN = 26
# __TIME_T_TYPE = __SYSCALL_SLONG_TYPE # alias
NI_PFI_OUTPUT_I_ATRIG = 17
NI_PFI_OUTPUT_PFI_DO = 16
NI_PFI_OUTPUT_FREQ_OUT = 15
NI_PFI_OUTPUT_GOUT0 = 13
NI_PFI_OUTPUT_AI_EXT_MUX_CLK = 12
NI_PFI_OUTPUT_EXT_STROBE = 11
NI_PFI_OUTPUT_G_GATE0 = 10
# __SLONG32_TYPE = int # alias
NI_PFI_OUTPUT_AI_START_PULSE = 8
def CR_PACK_FLAGS(chan,range,aref,flags): return (CR_PACK(chan, range, aref) | ((flags) & CR_FLAGS_MASK)) # macro
# __RLIM_T_TYPE = __SYSCALL_ULONG_TYPE # alias
NI_PFI_OUTPUT_AO_UPDATE_N = 6
NI_PFI_OUTPUT_G_GATE1 = 5
# __PID_T_TYPE = __S32_TYPE # alias
NI_PFI_OUTPUT_AI_CONVERT = 3
NI_PFI_OUTPUT_AI_START2 = 2
NI_PFI_OUTPUT_AI_START1 = 1
NI_PFI_OUTPUT_PFI_DEFAULT = 0
NI_GPCT_INDEX_ENABLE_BIT = 4194304
# __KEY_T_TYPE = __S32_TYPE # alias
# __INO_T_TYPE = __SYSCALL_ULONG_TYPE # alias
NI_GPCT_AI_START2_GATE_SELECT = 18
NI_GPCT_INDEX_PHASE_LOW_A_HIGH_B_BITS = 1048576
NI_FREQ_OUT_TIMEBASE_1_DIV_2_CLOCK_SRC = 0
COMEDI_INPUT = 0
NI_RTSI_OUTPUT_RGOUT0 = 7
NI_RTSI_OUTPUT_G_GATE0 = 6
NI_RTSI_OUTPUT_G_SRC0 = 5
NI_RTSI_OUTPUT_DACUPDN = 3
NI_CDIO_SCAN_BEGIN_SRC_DIO_CHANGE_DETECT_IRQ = 33
NI_RTSI_OUTPUT_SCLKG = 2
NI_RTSI_OUTPUT_ADR_START2 = 1
NI_RTSI_OUTPUT_ADR_START1 = 0
NI_GPCT_COUNTING_MODE_TWO_PULSE_BITS = 262144
__uid_t = c_uint
_IO_uid_t = __uid_t # alias
NI_GPCT_COUNTING_MODE_QUADRATURE_X4_BITS = 196608
NI_CDIO_SCAN_BEGIN_SRC_ANALOG_TRIGGER = 30
NI_GPCT_COUNTING_MODE_NORMAL_BITS = 0
NI_CDIO_SCAN_BEGIN_SRC_PXI_STAR_TRIGGER = 20
NI_CDIO_SCAN_BEGIN_SRC_AI_CONVERT = 19
NI_GPCT_LOADING_ON_TC_BIT = 4096
NI_GPCT_DISARM_AT_TC_OR_GATE_BITS = 3072
NI_GPCT_DISARM_AT_GATE_BITS = 2048
NI_GPCT_LOAD_B_SELECT_BIT = 128
NI_GPCT_TIMEBASE_1_CLOCK_SRC_BITS = 0
NI_GPCT_STOP_ON_GATE_OR_SECOND_TC_BITS = 64
NI_GPCT_STOP_ON_GATE_OR_TC_BITS = 32
NI_GPCT_EDGE_GATE_STARTS_STOPS_BITS = 0
AMPLC_DIO_CLK_10KHZ = 4
COMEDI_OOR_NAN = 1
COMEDI_OOR_NUMBER = 0
AMPLC_DIO_CLK_100KHZ = 3
class _G_fpos_t(Structure):
    pass
_G_fpos_t._fields_ = [
    ('__pos', __off_t),
    ('__state', __mbstate_t),
]
_IO_fpos_t = _G_fpos_t # alias
# __ID_T_TYPE = __U32_TYPE # alias
# __GID_T_TYPE = __U32_TYPE # alias
# __FSWORD_T_TYPE = __SYSCALL_SLONG_TYPE # alias
# __FSFILCNT_T_TYPE = __SYSCALL_ULONG_TYPE # alias
# __FSBLKCNT_T_TYPE = __SYSCALL_ULONG_TYPE # alias
INSN_CONFIG_SET_COUNTER_MODE = 4097
__LITTLE_ENDIAN = 1234 # Variable c_int '1234'
__BYTE_ORDER = __LITTLE_ENDIAN # alias
__FLOAT_WORD_ORDER = __BYTE_ORDER # alias
# __DEV_T_TYPE = __UQUAD_TYPE # alias
# __DADDR_T_TYPE = __S32_TYPE # alias
I8254_BCD = 1
# __BLKSIZE_T_TYPE = __SYSCALL_SLONG_TYPE # alias
I8254_MODE2 = 4
# __BLKCNT_T_TYPE = __SYSCALL_SLONG_TYPE # alias
I8254_MODE0 = 0
_STAT_VER_LINUX = 1 # Variable c_int '1'
_STAT_VER = _STAT_VER_LINUX # alias
class __va_list_tag(Structure):
    pass
__va_list_tag._fields_ = [
]
__gnuc_va_list = __va_list_tag * 1
_IO_va_list = __gnuc_va_list # alias
AMPLC_DIO_CLK_1MHZ = 2
__pid_t = c_int
_IO_pid_t = __pid_t # alias
# _IO_file_flags = _flags # alias
CMDF_WRITE = 64 # Variable c_int '64'
TRIG_WRITE = CMDF_WRITE # alias
TIOCM_CAR = 64 # Variable c_int '64'
TIOCM_CD = TIOCM_CAR # alias
FIONREAD = 21531 # Variable c_int '21531'
TIOCINQ = FIONREAD # alias
__S_IREAD = 256 # Variable c_int '256'
S_IRUSR = __S_IREAD # alias
__S_IFSOCK = 49152 # Variable c_int '49152'
S_IFSOCK = __S_IFSOCK # alias
__S_IFLNK = 40960 # Variable c_int '40960'
S_IFLNK = __S_IFLNK # alias
__S_IFIFO = 4096 # Variable c_int '4096'
S_IFIFO = __S_IFIFO # alias
AMPLC_DIO_CLK_10MHZ = 1
__S_IFBLK = 24576 # Variable c_int '24576'
S_IFBLK = __S_IFBLK # alias
SIOCGIFINDEX = 35123 # Variable c_int '35123'
SIOGIFINDEX = SIOCGIFINDEX # alias
AMPLC_DIO_CLK_CLKN = 0
NI_MIO_PLL_RTSI0_CLOCK = 4
AMPLC_DIO_GAT_RESERVED7 = 7
AMPLC_DIO_GAT_RESERVED6 = 6
NI_GPCT_OR_GATE_BIT = 268435456
NI_GPCT_RELOAD_SOURCE_FIXED_BITS = 0
NI_GPCT_RELOAD_SOURCE_MASK = 201326592
NI_GPCT_COUNTING_DIRECTION_UP_BITS = 16777216
NI_GPCT_COUNTING_DIRECTION_DOWN_BITS = 0
NI_GPCT_COUNTING_DIRECTION_MASK = 50331648
_G_va_list = __gnuc_va_list # alias
NI_FREQ_OUT_TIMEBASE_2_CLOCK_SRC = 1
NI_GPCT_INDEX_PHASE_LOW_A_LOW_B_BITS = 0
NI_CDIO_SCAN_BEGIN_SRC_FREQ_OUT = 32
NI_CDIO_SCAN_BEGIN_SRC_AO_UPDATE = 31
NI_GPCT_COUNTING_MODE_QUADRATURE_X2_BITS = 131072
NI_CDIO_SCAN_BEGIN_SRC_G1_OUT = 29
NI_CDIO_SCAN_BEGIN_SRC_G0_OUT = 28
NI_GPCT_LOADING_ON_GATE_BIT = 16384
NI_CDIO_SCAN_BEGIN_SRC_AI_START = 18
NI_CDIO_SCAN_BEGIN_SRC_GROUND = 0
NI_GPCT_DISARM_AT_TC_BITS = 1024
NI_GPCT_NO_HARDWARE_DISARM_BITS = 0
NI_GPCT_HARDWARE_DISARM_MASK = 3072
NI_GPCT_OUTPUT_TC_OR_GATE_TOGGLE_BITS = 768
NI_GPCT_OUTPUT_TC_TOGGLE_BITS = 512
NI_GPCT_OUTPUT_TC_PULSE_BITS = 256
NI_GPCT_OUTPUT_MODE_MASK = 768
NI_GPCT_STOP_ON_GATE_BITS = 0
NI_GPCT_STOP_MODE_MASK = 96
NI_GPCT_EDGE_GATE_NO_STARTS_NO_STOPS_BITS = 24
NI_GPCT_EDGE_GATE_STARTS_BITS = 16
NI_GPCT_EDGE_GATE_STOPS_STARTS_BITS = 8
NI_GPCT_EDGE_GATE_MODE_MASK = 24
NI_GPCT_GATE_ON_BOTH_EDGES_BIT = 4
def __GNUC_PREREQ(maj,min): return ((__GNUC__ << 16) + __GNUC_MINOR__ >= ((maj) << 16) + (min)) # macro
NI_MIO_PLL_PXI10_CLOCK = 3
NI_MIO_PLL_PXI_STAR_TRIGGER_CLOCK = 2
NI_MIO_RTSI_CLOCK = 1
NI_MIO_INTERNAL_CLOCK = 0
AMPLC_DIO_GAT_RESERVED4 = 4
AMPLC_DIO_GAT_NOUTNM2 = 3
AMPLC_DIO_GAT_GATN = 2
AMPLC_DIO_GAT_GND = 1
AMPLC_DIO_GAT_VCC = 0
NI_GPCT_COUNTING_MODE_MASK = 458752
COMEDI_OUTPUT = 1
NI_GPCT_INVERT_CLOCK_SRC_BIT = -2147483648
NI_GPCT_PRESCALE_X8_CLOCK_SRC_BITS = 536870912
NI_GPCT_PRESCALE_X2_CLOCK_SRC_BITS = 268435456
NI_GPCT_NO_PRESCALE_CLOCK_SRC_BITS = 0
NI_GPCT_PRESCALE_MODE_CLOCK_SRC_MASK = 805306368
__POSIX_FADV_NOREUSE = 5 # Variable c_int '5'
POSIX_FADV_NOREUSE = __POSIX_FADV_NOREUSE # alias
__POSIX_FADV_DONTNEED = 4 # Variable c_int '4'
POSIX_FADV_DONTNEED = __POSIX_FADV_DONTNEED # alias
__PDP_ENDIAN = 3412 # Variable c_int '3412'
PDP_ENDIAN = __PDP_ENDIAN # alias
__O_TMPFILE = 4259840 # Variable c_int '4259840'
O_TMPFILE = __O_TMPFILE # alias
O_SYNC = 1052672 # Variable c_int '1052672'
O_RSYNC = O_SYNC # alias
__O_PATH = 2097152 # Variable c_int '2097152'
O_PATH = __O_PATH # alias
__O_NOFOLLOW = 131072 # Variable c_int '131072'
O_NOFOLLOW = __O_NOFOLLOW # alias
__O_NOATIME = 262144 # Variable c_int '262144'
O_NOATIME = __O_NOATIME # alias
O_NONBLOCK = 2048 # Variable c_int '2048'
O_NDELAY = O_NONBLOCK # alias
__O_LARGEFILE = 0 # Variable c_int '0'
O_LARGEFILE = __O_LARGEFILE # alias
O_FSYNC = O_SYNC # alias
__O_DSYNC = 4096 # Variable c_int '4096'
O_DSYNC = __O_DSYNC # alias
__O_DIRECTORY = 65536 # Variable c_int '65536'
O_DIRECTORY = __O_DIRECTORY # alias
__O_DIRECT = 16384 # Variable c_int '16384'
O_DIRECT = __O_DIRECT # alias
__O_CLOEXEC = 524288 # Variable c_int '524288'
O_CLOEXEC = __O_CLOEXEC # alias
# NULL = __null # alias
__NFDBITS = 64 # Variable c_int '64'
NFDBITS = __NFDBITS # alias
LITTLE_ENDIAN = __LITTLE_ENDIAN # alias
__F_SETSIG = 10 # Variable c_int '10'
F_SETSIG = __F_SETSIG # alias
__F_SETOWN_EX = 15 # Variable c_int '15'
F_SETOWN_EX = __F_SETOWN_EX # alias
__F_SETOWN = 8 # Variable c_int '8'
F_SETOWN = __F_SETOWN # alias
__F_GETSIG = 11 # Variable c_int '11'
F_GETSIG = __F_GETSIG # alias
__F_GETOWN_EX = 16 # Variable c_int '16'
F_GETOWN_EX = __F_GETOWN_EX # alias
__F_GETOWN = 9 # Variable c_int '9'
F_GETOWN = __F_GETOWN # alias
FNONBLOCK = O_NONBLOCK # alias
FNDELAY = O_NDELAY # alias
FFSYNC = O_FSYNC # alias
__FD_SETSIZE = 1024 # Variable c_int '1024'
FD_SETSIZE = __FD_SETSIZE # alias
O_ASYNC = 8192 # Variable c_int '8192'
FASYNC = O_ASYNC # alias
O_APPEND = 1024 # Variable c_int '1024'
FAPPEND = O_APPEND # alias
CR_ALT_FILTER = 67108864 # Variable c_int '67108864'
CR_DITHER = CR_ALT_FILTER # alias
CR_DEGLITCH = CR_ALT_FILTER # alias
CREPRINT = 18 # Variable c_int '18'
CRPRNT = CREPRINT # alias
CDISCARD = 15 # Variable c_int '15'
CFLUSH = CDISCARD # alias
CEOF = 4 # Variable c_int '4'
CEOT = CEOF # alias
CEOL = '\x00' # Variable c_char "'\\000'"
CBRK = CEOL # alias
BYTE_ORDER = __BYTE_ORDER # alias
BUFSIZ = _IO_BUFSIZ # alias
__BIG_ENDIAN = 4321 # Variable c_int '4321'
BIG_ENDIAN = __BIG_ENDIAN # alias
NI_660X_PFI_OUTPUT_DIO = 2
COMEDI_OPENDRAIN = 2
NI_660X_PFI_OUTPUT_COUNTER = 1
__S_IWRITE = 128 # Variable c_int '128'
S_IWUSR = __S_IWRITE # alias
# def __FD_ELT(d): return __extension__ ({ long int __d = (d); (__builtin_constant_p (__d) ? (0 <= __d && __d < __FD_SETSIZE ? (__d / __NFDBITS) : __fdelt_warn (__d)) : __fdelt_chk (__d)); }) # macro
I8254_BINARY = 0
INSN_CONFIG_GET_PWM_OUTPUT = 30
AMPLC_DIO_GAT_RESERVED5 = 5
I8254_MODE5 = 10
__S_ISGID = 1024 # Variable c_int '1024'
S_ISGID = __S_ISGID # alias
NI_GPCT_COUNTING_DIRECTION_HW_UP_DOWN_BITS = 33554432
NI_GPCT_FILTER_10x_TIMEBASE_1 = 4
NI_GPCT_FILTER_100x_TIMEBASE_1 = 2
I8254_MODE1 = 2
NI_GPCT_FILTER_2x_TIMEBASE_3 = 6
NI_GPCT_FILTER_2x_TIMEBASE_1 = 5
NI_GPCT_FILTER_20x_TIMEBASE_1 = 3
NI_GPCT_FILTER_TIMEBASE_3_SYNC = 1
NI_GPCT_FILTER_OFF = 0
_IO_UPPERCASE = 512 # Variable c_int '512'
_ATFILE_SOURCE = 1 # Variable c_int '1'
EOF = -1 # Variable c_int '-0x00000000000000001'
AREF_OTHER = 3 # Variable c_int '3'
DN_ATTRIB = 32 # Variable c_int '32'
_IO_USER_LOCK = 32768 # Variable c_int '32768'
UTIME_OMIT = 1073741822 # Variable c_long '1073741822l'
__INO_T_MATCHES_INO64_T = 1 # Variable c_int '1'
SDF_INTERNAL = 262144 # Variable c_int '262144'
TRIG_DEGLITCH = 4 # Variable c_int '4'
F_UNLCK = 2 # Variable c_int '2'
TRIG_ROUND_DOWN = 65536 # Variable c_int '65536'
_G_HAVE_MREMAP = 1 # Variable c_int '1'
SIOCPROTOPRIVATE = 35296 # Variable c_int '35296'
__SIZEOF_PTHREAD_CONDATTR_T = 4 # Variable c_int '4'
TIOCMGET = 21525 # Variable c_int '21525'
IOCSIZE_SHIFT = 16 # Variable c_int '16'
F_SETLKW = 7 # Variable c_int '7'
F_GETLEASE = 1025 # Variable c_int '1025'
F_DUPFD_CLOEXEC = 1030 # Variable c_int '1030'
__time_t_defined = 1 # Variable c_int '1'
TIOCSERGSTRUCT = 21592 # Variable c_int '21592'
TIOCMSET = 21528 # Variable c_int '21528'
TRIG_NOW = 2 # Variable c_int '2'
_POSIX_SOURCE = 1 # Variable c_int '1'
F_DUPFD = 0 # Variable c_int '0'
SIOCADDRT = 35083 # Variable c_int '35083'
GPCT_SINGLE_PULSE_OUT = 1024 # Variable c_int '1024'
SIOCGIFPFLAGS = 35125 # Variable c_int '35125'
_DEFAULT_SOURCE = 1 # Variable c_int '1'
SDF_GROUND = 1048576 # Variable c_int '1048576'
COMEDI_CHANINFO = 2150654979L # Variable c_ulong '2150654979ul'
TIOCSERGETLSR = 21593 # Variable c_int '21593'
RF_EXTERNAL = 256 # Variable c_int '256'
SIOCSIFMTU = 35106 # Variable c_int '35106'
UNIT_volt = 0 # Variable c_int '0'
INSN_MASK_READ = 67108864 # Variable c_int '67108864'
__USE_POSIX199309 = 1 # Variable c_int '1'
TIOCGPTLCK = 2147767353L # Variable c_ulong '2147767353ul'
TRIG_ROUND_NEAREST = 0 # Variable c_int '0'
GPCT_INT_CLOCK = 1 # Variable c_int '1'
COMEDI_CB_OVERFLOW = 32 # Variable c_int '32'
_MKNOD_VER_LINUX = 0 # Variable c_int '0'
CSTATUS = '\x00' # Variable c_char "'\\000'"
COMEDI_NAMELEN = 20 # Variable c_int '20'
TRIG_BOGUS = 1 # Variable c_int '1'
_IO_SHOWBASE = 128 # Variable c_int '128'
TIOCMIWAIT = 21596 # Variable c_int '21596'
O_RDWR = 2 # Variable c_int '2'
_G_HAVE_MMAP = 1 # Variable c_int '1'
_IOC_NONE = 0L # Variable c_uint '0u'
F_TLOCK = 2 # Variable c_int '2'
__WORDSIZE_TIME64_COMPAT32 = 1 # Variable c_int '1'
CR_FLAGS_MASK = 4227858432L # Variable c_uint '4227858432u'
__SIZEOF_PTHREAD_BARRIER_T = 32 # Variable c_int '32'
_IOS_BIN = 128 # Variable c_int '128'
TIOCM_DTR = 2 # Variable c_int '2'
_IO_SKIPWS = 1 # Variable c_int '1'
S_IRWXG = 56 # Variable c_int '56'
TRIG_DITHER = 2 # Variable c_int '2'
F_SETLK64 = 6 # Variable c_int '6'
_STAT_VER_KERNEL = 0 # Variable c_int '0'
S_IRWXO = 7 # Variable c_int '7'
_IO_SCIENTIFIC = 2048 # Variable c_int '2048'
_IOC_SIZEMASK = 16383 # Variable c_int '16383'
S_IRWXU = 448 # Variable c_int '448'
GPCT_HWUD = 32 # Variable c_int '32'
AT_EACCESS = 512 # Variable c_int '512'
TIOCCONS = 21533 # Variable c_int '21533'
_LARGEFILE_SOURCE = 1 # Variable c_int '1'
TIOCSCTTY = 21518 # Variable c_int '21518'
CR_ALT_SOURCE = 134217728 # Variable c_int '134217728'
F_OK = 0 # Variable c_int '0'
TIOCSSOFTCAR = 21530 # Variable c_int '21530'
_IO_DEC = 16 # Variable c_int '16'
TIOCGPGRP = 21519 # Variable c_int '21519'
TIOCPKT_STOP = 4 # Variable c_int '4'
SDF_CMD_WRITE = 16384 # Variable c_int '16384'
SIOCDELDLCI = 35201 # Variable c_int '35201'
_IO_LINE_BUF = 512 # Variable c_int '512'
COMEDILIB_VERSION_MINOR = 10 # Variable c_int '10'
_IOS_TRUNC = 16 # Variable c_int '16'
O_WRONLY = 1 # Variable c_int '1'
_ENDIAN_H = 1 # Variable c_int '1'
_IOC_SIZESHIFT = 16 # Variable c_int '16'
SIOCSIFDSTADDR = 35096 # Variable c_int '35096'
__USE_FORTIFY_LEVEL = 2 # Variable c_int '2'
SIOCGIFSLAVE = 35113 # Variable c_int '35113'
SDF_LSAMPL = 268435456 # Variable c_int '268435456'
CR_EDGE = 1073741824 # Variable c_int '1073741824'
COMEDI_DEVCONFIG = 1083466752L # Variable c_ulong '1083466752ul'
__USE_XOPEN_EXTENDED = 1 # Variable c_int '1'
SEEK_END = 2 # Variable c_int '2'
N_HDLC = 13 # Variable c_int '13'
NI_GPCT_INDEX_PHASE_BITSHIFT = 20 # Variable c_int '20'
_IOC_NRMASK = 255 # Variable c_int '255'
TRIG_TIME = 8 # Variable c_int '8'
SIOCSIFBR = 35137 # Variable c_int '35137'
F_GETLK64 = 5 # Variable c_int '5'
TCGETS = 21505 # Variable c_int '21505'
_IO_BOOLALPHA = 65536 # Variable c_int '65536'
CMDF_RAWDATA = 128 # Variable c_int '128'
N_TTY = 0 # Variable c_int '0'
_IO_UNITBUF = 8192 # Variable c_int '8192'
GPCT_SINGLE_PERIOD = 128 # Variable c_int '128'
SIOCGIFCOUNT = 35128 # Variable c_int '35128'
COMEDI_DEVCONF_AUX_DATA1_LENGTH = 27 # Variable c_int '27'
O_CREAT = 64 # Variable c_int '64'
SDF_LOCK_OWNER = 8 # Variable c_int '8'
__WORDSIZE = 64 # Variable c_int '64'
AT_NO_AUTOMOUNT = 2048 # Variable c_int '2048'
SDF_OTHER = 8388608 # Variable c_int '8388608'
GPCT_SET_SOURCE = 2 # Variable c_int '2'
UNIT_none = 2 # Variable c_int '2'
GPCT_UP = 8 # Variable c_int '8'
_XOPEN_SOURCE = 700 # Variable c_int '700'
COMEDI_DEVCONF_AUX_DATA_HI = 29 # Variable c_int '29'
SIOCSIFFLAGS = 35092 # Variable c_int '35092'
TIOCSTI = 21522 # Variable c_int '21522'
__USE_ISOC95 = 1 # Variable c_int '1'
TIOCPKT = 21536 # Variable c_int '21536'
N_R3964 = 9 # Variable c_int '9'
__GLIBC__ = 2 # Variable c_int '2'
GPCT_CONT_PULSE_OUT = 512 # Variable c_int '512'
__USE_ISOC99 = 1 # Variable c_int '1'
CSTART = 17 # Variable c_int '17'
SIOCGIFTXQLEN = 35138 # Variable c_int '35138'
N_MOUSE = 2 # Variable c_int '2'
COMEDI_DEVCONF_AUX_DATA_LO = 30 # Variable c_int '30'
SDF_DITHER = 16777216 # Variable c_int '16777216'
SPLICE_F_NONBLOCK = 2 # Variable c_int '2'
_IOC_TYPESHIFT = 8 # Variable c_int '8'
_IONBF = 2 # Variable c_int '2'
TIOCGETD = 21540 # Variable c_int '21540'
F_GETPIPE_SZ = 1032 # Variable c_int '1032'
N_HCI = 15 # Variable c_int '15'
F_SETLKW64 = 7 # Variable c_int '7'
_BITS_UIO_H = 1 # Variable c_int '1'
F_SETPIPE_SZ = 1031 # Variable c_int '1031'
FALLOC_FL_PUNCH_HOLE = 2 # Variable c_int '2'
TIOCSERSETMULTI = 21595 # Variable c_int '21595'
COMEDI_SUBDINFO = 2152227842L # Variable c_ulong '2152227842ul'
_IO_RIGHT = 4 # Variable c_int '4'
COMEDI_EV_STOP = 4194304 # Variable c_int '4194304'
TIOCSER_TEMT = 1 # Variable c_int '1'
__USE_ATFILE = 1 # Variable c_int '1'
SDF_MODE4 = 2048 # Variable c_int '2048'
TMP_MAX = 238328 # Variable c_int '238328'
SDF_MODE2 = 512 # Variable c_int '512'
SDF_MODE3 = 1024 # Variable c_int '1024'
_FCNTL_H = 1 # Variable c_int '1'
TIOCSPGRP = 21520 # Variable c_int '21520'
INSN_WAIT = 167772165 # Variable c_int '167772165'
SIOCGARP = 35156 # Variable c_int '35156'
TIOCPKT_FLUSHWRITE = 2 # Variable c_int '2'
__USE_POSIX = 1 # Variable c_int '1'
_IO_NO_WRITES = 8 # Variable c_int '8'
SIOCSIFSLAVE = 35120 # Variable c_int '35120'
INSN_CONFIG = 201326595 # Variable c_int '201326595'
_IOC_DIRMASK = 3 # Variable c_int '3'
__SIZEOF_PTHREAD_MUTEXATTR_T = 4 # Variable c_int '4'
__FILE_defined = 1 # Variable c_int '1'
INSN_GTOD = 100663300 # Variable c_int '100663300'
SYNC_FILE_RANGE_WAIT_AFTER = 4 # Variable c_int '4'
SIOCGIFBR = 35136 # Variable c_int '35136'
_IO_NO_READS = 4 # Variable c_int '4'
TIOCSRS485 = 21551 # Variable c_int '21551'
__GLIBC_MINOR__ = 19 # Variable c_int '19'
TIOCM_DSR = 256 # Variable c_int '256'
__clockid_t_defined = 1 # Variable c_int '1'
SEEK_SET = 0 # Variable c_int '0'
COMEDI_BUFINFO = 3224134670L # Variable c_ulong '3224134670ul'
TIOCGSID = 21545 # Variable c_int '21545'
_SYS_SELECT_H = 1 # Variable c_int '1'
TRIG_INVALID = 0 # Variable c_int '0'
SIOCSIFLINK = 35089 # Variable c_int '35089'
_SYS_TYPES_H = 1 # Variable c_int '1'
DN_RENAME = 16 # Variable c_int '16'
COMEDI_MAJOR = 98 # Variable c_int '98'
_IOC_TYPEMASK = 255 # Variable c_int '255'
GPCT_NO_GATE = 4 # Variable c_int '4'
_IO_ERR_SEEN = 32 # Variable c_int '32'
UNIT_mA = 1 # Variable c_int '1'
TCGETX = 21554 # Variable c_int '21554'
__USE_GNU = 1 # Variable c_int '1'
TRIG_WAKE_EOS = 32 # Variable c_int '32'
SDF_RUNNING = 134217728 # Variable c_int '134217728'
TCSETA = 21510 # Variable c_int '21510'
F_RDLCK = 0 # Variable c_int '0'
SIOCSIFMEM = 35104 # Variable c_int '35104'
__USE_LARGEFILE64 = 1 # Variable c_int '1'
TCSETX = 21555 # Variable c_int '21555'
TCGETA = 21509 # Variable c_int '21509'
N_STRIP = 4 # Variable c_int '4'
_G_IO_IO_FILE_VERSION = 131073 # Variable c_int '131073'
TCSETS = 21506 # Variable c_int '21506'
TIOCSBRK = 21543 # Variable c_int '21543'
_POSIX_C_SOURCE = 200809 # Variable c_long '200809l'
SIOCGIFMTU = 35105 # Variable c_int '35105'
TIOCSERCONFIG = 21587 # Variable c_int '21587'
SIOCGIFBRDADDR = 35097 # Variable c_int '35097'
__USE_SVID = 1 # Variable c_int '1'
TRIG_TIMER = 16 # Variable c_int '16'
TIOCPKT_NOSTOP = 16 # Variable c_int '16'
_IO_IS_APPENDING = 4096 # Variable c_int '4096'
SDF_CMD_READ = 32768 # Variable c_int '32768'
_IOC_WRITE = 1L # Variable c_uint '1u'
COMEDI_CMDTEST = 2152752138L # Variable c_ulong '2152752138ul'
L_ctermid = 9 # Variable c_int '9'
_IO_INTERNAL = 8 # Variable c_int '8'
__SIZEOF_PTHREAD_RWLOCK_T = 56 # Variable c_int '56'
CDSUSP = 25 # Variable c_int '25'
FIONBIO = 21537 # Variable c_int '21537'
_IOC_TYPEBITS = 8 # Variable c_int '8'
_IOS_NOCREATE = 32 # Variable c_int '32'
_IO_TIED_PUT_GET = 1024 # Variable c_int '1024'
TIOCSLCKTRMIOS = 21591 # Variable c_int '21591'
CKILL = 21 # Variable c_int '21'
COMEDI_DEVCONF_AUX_DATA_LENGTH = 31 # Variable c_int '31'
SDF_MAXDATA = 16 # Variable c_int '16'
SDF_PACKED = 536870912 # Variable c_int '536870912'
__USE_EXTERN_INLINES = 1 # Variable c_int '1'
__SIZEOF_PTHREAD_COND_T = 48 # Variable c_int '48'
_FEATURES_H = 1 # Variable c_int '1'
LOCK_SH = 1 # Variable c_int '1'
SEEK_DATA = 3 # Variable c_int '3'
_IOS_INPUT = 1 # Variable c_int '1'
SIOCSIFHWADDR = 35108 # Variable c_int '35108'
SIOCGIFMAP = 35184 # Variable c_int '35184'
UTIME_NOW = 1073741823 # Variable c_long '1073741823l'
SIOCSIFHWBROADCAST = 35127 # Variable c_int '35127'
_BITS_TYPES_H = 1 # Variable c_int '1'
_IOC_NRSHIFT = 0 # Variable c_int '0'
LOCK_READ = 64 # Variable c_int '64'
SIOCSIFENCAP = 35110 # Variable c_int '35110'
TIOCSERSWILD = 21589 # Variable c_int '21589'
S_IXOTH = 1 # Variable c_int '1'
SIOCSIFMAP = 35185 # Variable c_int '35185'
SIOCSIFPFLAGS = 35124 # Variable c_int '35124'
TIOCSWINSZ = 21524 # Variable c_int '21524'
TRIG_NONE = 1 # Variable c_int '1'
TRIG_OTHER = 256 # Variable c_int '256'
SIOCDIFADDR = 35126 # Variable c_int '35126'
SIOCGIFNETMASK = 35099 # Variable c_int '35099'
COMEDI_INSNLIST = 2148557835L # Variable c_ulong '2148557835ul'
TIOCSERGWILD = 21588 # Variable c_int '21588'
_XOPEN_SOURCE_EXTENDED = 1 # Variable c_int '1'
GPCT_SET_OPERATION = 16 # Variable c_int '16'
_IO_UNBUFFERED = 2 # Variable c_int '2'
LOCK_UN = 8 # Variable c_int '8'
F_LOCK = 1 # Variable c_int '1'
TIOCMBIS = 21526 # Variable c_int '21526'
SDF_LOCKED = 4 # Variable c_int '4'
COMEDILIB_VERSION_MICRO = 1 # Variable c_int '1'
TCSETXW = 21557 # Variable c_int '21557'
TIOCPKT_FLUSHREAD = 1 # Variable c_int '1'
_IOS_ATEND = 4 # Variable c_int '4'
O_RDONLY = 0 # Variable c_int '0'
GPCT_SIMPLE_EVENT = 64 # Variable c_int '64'
TIOCMBIC = 21527 # Variable c_int '21527'
CSUSP = 26 # Variable c_int '26'
COMEDI_MIN_SPEED = 4294967295L # Variable c_uint '4294967295u'
TCSETXF = 21556 # Variable c_int '21556'
TIOCPKT_DOSTOP = 32 # Variable c_int '32'
NCC = 8 # Variable c_int '8'
AT_REMOVEDIR = 512 # Variable c_int '512'
N_PROFIBUS_FDL = 10 # Variable c_int '10'
AREF_COMMON = 1 # Variable c_int '1'
SPLICE_F_GIFT = 8 # Variable c_int '8'
_BSD_SOURCE = 1 # Variable c_int '1'
__FD_ZERO_STOS = 'stosq' # Variable STRING '(const char*)"stosq"'
F_ULOCK = 0 # Variable c_int '0'
FIONCLEX = 21584 # Variable c_int '21584'
__GNU_LIBRARY__ = 6 # Variable c_int '6'
_BITS_TYPESIZES_H = 1 # Variable c_int '1'
_IO_USER_BUF = 1 # Variable c_int '1'
SIOCSIFNAME = 35107 # Variable c_int '35107'
F_WRLCK = 1 # Variable c_int '1'
SDF_READABLE = 65536 # Variable c_int '65536'
TRIG_FOLLOW = 4 # Variable c_int '4'
TCFLSH = 21515 # Variable c_int '21515'
NI_GPCT_COUNTING_MODE_SHIFT = 16 # Variable c_int '16'
AT_SYMLINK_NOFOLLOW = 256 # Variable c_int '256'
TIOCOUTQ = 21521 # Variable c_int '21521'
SIOCGIFNAME = 35088 # Variable c_int '35088'
N_AX25 = 5 # Variable c_int '5'
TIOCM_ST = 8 # Variable c_int '8'
COMEDI_CB_ERROR = 16 # Variable c_int '16'
TIOCM_SR = 16 # Variable c_int '16'
GPCT_SINGLE_PW = 256 # Variable c_int '256'
LOCK_MAND = 32 # Variable c_int '32'
GPCT_RESET = 1 # Variable c_int '1'
TIOCSETD = 21539 # Variable c_int '21539'
N_6PACK = 7 # Variable c_int '7'
LOCK_WRITE = 128 # Variable c_int '128'
_G_config_h = 1 # Variable c_int '1'
____mbstate_t_defined = 1 # Variable c_int '1'
TIOCPKT_IOCTL = 64 # Variable c_int '64'
_IO_LEFT = 2 # Variable c_int '2'
_IO_FLAGS2_MMAP = 1 # Variable c_int '1'
DN_DELETE = 8 # Variable c_int '8'
DN_MODIFY = 2 # Variable c_int '2'
CSTOP = 19 # Variable c_int '19'
CS_MAX_AREFS_LENGTH = 4 # Variable c_int '4'
COMEDI_CANCEL = 25607L # Variable c_uint '25607u'
FOPEN_MAX = 16 # Variable c_int '16'
_IO_DELETE_DONT_CLOSE = 64 # Variable c_int '64'
GPCT_SET_GATE = 4 # Variable c_int '4'
F_GETLK = 5 # Variable c_int '5'
GPCT_EXT_PIN = 2 # Variable c_int '2'
CMIN = 1 # Variable c_int '1'
SIOCSIFBRDADDR = 35098 # Variable c_int '35098'
TCXONC = 21514 # Variable c_int '21514'
__USE_LARGEFILE = 1 # Variable c_int '1'
__USE_XOPEN = 1 # Variable c_int '1'
TRIG_ROUND_MASK = 196608 # Variable c_int '196608'
DN_CREATE = 4 # Variable c_int '4'
COMEDI_UNLOCK = 25606L # Variable c_uint '25606u'
TIOCM_LE = 1 # Variable c_int '1'
COMEDI_DEVCONF_AUX_DATA2_LENGTH = 26 # Variable c_int '26'
SIOCGIFMEM = 35103 # Variable c_int '35103'
N_IRDA = 11 # Variable c_int '11'
TIOCNXCL = 21517 # Variable c_int '21517'
SYNC_FILE_RANGE_WRITE = 2 # Variable c_int '2'
SIOCGIFFLAGS = 35091 # Variable c_int '35091'
SDF_DEGLITCH = 33554432 # Variable c_int '33554432'
AT_SYMLINK_FOLLOW = 1024 # Variable c_int '1024'
__USE_XOPEN2K = 1 # Variable c_int '1'
CLNEXT = 22 # Variable c_int '22'
SDF_RANGETYPE = 64 # Variable c_int '64'
O_TRUNC = 512 # Variable c_int '512'
_IO_LINKED = 128 # Variable c_int '128'
__timespec_defined = 1 # Variable c_int '1'
N_SYNC_PPP = 14 # Variable c_int '14'
__USE_POSIX2 = 1 # Variable c_int '1'
SDF_RT = 524288 # Variable c_int '524288'
TIOCEXCL = 21516 # Variable c_int '21516'
SDF_FLAGS = 32 # Variable c_int '32'
__SIZEOF_PTHREAD_BARRIERATTR_T = 4 # Variable c_int '4'
GPCT_ARM = 32 # Variable c_int '32'
SDF_SOFT_CALIBRATED = 8192 # Variable c_int '8192'
L_tmpnam = 20 # Variable c_int '20'
SIOCGIFENCAP = 35109 # Variable c_int '35109'
__PTHREAD_RWLOCK_INT_FLAGS_SHARED = 1 # Variable c_int '1'
_IO_DONT_CLOSE = 32768 # Variable c_int '32768'
F_SETFD = 2 # Variable c_int '2'
_IOC_DIRSHIFT = 30 # Variable c_int '30'
INSN_WRITE = 134217729 # Variable c_int '134217729'
F_SETFL = 4 # Variable c_int '4'
_IO_BAD_SEEN = 16384 # Variable c_int '16384'
__USE_MISC = 1 # Variable c_int '1'
COMEDI_TRIG = 3225445380L # Variable c_ulong '3225445380ul'
__BIT_TYPES_DEFINED__ = 1 # Variable c_int '1'
TIOCSPTLCK = 1074025521L # Variable c_ulong '1074025521ul'
S_IWOTH = 2 # Variable c_int '2'
F_TEST = 3 # Variable c_int '3'
GPCT_SET_DIRECTION = 8 # Variable c_int '8'
SIOCGRARP = 35169 # Variable c_int '35169'
__PTHREAD_MUTEX_HAVE_ELISION = 1 # Variable c_int '1'
SIOCSIFADDR = 35094 # Variable c_int '35094'
POSIX_FADV_SEQUENTIAL = 2 # Variable c_int '2'
S_IROTH = 4 # Variable c_int '4'
_IO_HEX = 64 # Variable c_int '64'
CQUIT = 28 # Variable c_int '28'
N_SLIP = 1 # Variable c_int '1'
__PTHREAD_MUTEX_HAVE_PREV = 1 # Variable c_int '1'
SPLICE_F_MORE = 4 # Variable c_int '4'
COMEDI_CMD = 2152752137L # Variable c_ulong '2152752137ul'
COMEDI_EV_START = 262144 # Variable c_int '262144'
_BITS_BYTESWAP_H = 1 # Variable c_int '1'
SIOCSRARP = 35170 # Variable c_int '35170'
FIOQSIZE = 21600 # Variable c_int '21600'
FILENAME_MAX = 4096 # Variable c_int '4096'
L_cuserid = 9 # Variable c_int '9'
_SYS_SYSMACROS_H = 1 # Variable c_int '1'
GPCT_DISARM = 64 # Variable c_int '64'
FIOCLEX = 21585 # Variable c_int '21585'
COMEDI_CB_EOBUF = 8 # Variable c_int '8'
LOCK_RW = 192 # Variable c_int '192'
__USE_POSIX199506 = 1 # Variable c_int '1'
W_OK = 2 # Variable c_int '2'
SEEK_HOLE = 4 # Variable c_int '4'
R_OK = 4 # Variable c_int '4'
COMEDI_DEVCONF_AUX_DATA3_LENGTH = 25 # Variable c_int '25'
FALLOC_FL_KEEP_SIZE = 1 # Variable c_int '1'
SDF_COMMON = 2097152 # Variable c_int '2097152'
_IO_SHOWPOINT = 256 # Variable c_int '256'
__USE_XOPEN2K8XSI = 1 # Variable c_int '1'
AREF_GROUND = 0 # Variable c_int '0'
_SYS_CDEFS_H = 1 # Variable c_int '1'
COMEDI_RANGEINFO = 2148557832L # Variable c_ulong '2148557832ul'
_OLD_STDIO_MAGIC = 4206624768L # Variable c_uint '4206624768u'
_IO_IS_FILEBUF = 8192 # Variable c_int '8192'
__SIZEOF_PTHREAD_ATTR_T = 56 # Variable c_int '56'
TIOCGSOFTCAR = 21529 # Variable c_int '21529'
TIOCNOTTY = 21538 # Variable c_int '21538'
_IOS_OUTPUT = 2 # Variable c_int '2'
TIOCGEXCL = 2147767360L # Variable c_ulong '2147767360ul'
TRIG_COUNT = 32 # Variable c_int '32'
_SYS_IOCTL_H = 1 # Variable c_int '1'
COMEDI_CB_BLOCK = 4 # Variable c_int '4'
INSN_READ = 67108864 # Variable c_int '67108864'
S_IXGRP = 8 # Variable c_int '8'
GPCT_DOWN = 16 # Variable c_int '16'
N_SMSBLOCK = 12 # Variable c_int '12'
O_EXCL = 128 # Variable c_int '128'
SIOCSIFTXQLEN = 35139 # Variable c_int '35139'
S_IWGRP = 16 # Variable c_int '16'
SDF_MMAP = 67108864 # Variable c_int '67108864'
COMEDI_EV_SCAN_BEGIN = 524288 # Variable c_int '524288'
__have_pthread_attr_t = 1 # Variable c_int '1'
UIO_MAXIOV = 1024 # Variable c_int '1024'
SIOCDELMULTI = 35122 # Variable c_int '35122'
__USE_XOPEN2KXSI = 1 # Variable c_int '1'
POSIX_FADV_RANDOM = 1 # Variable c_int '1'
COMEDI_MAX_NUM_POLYNOMIAL_COEFFICIENTS = 4 # Variable c_int '4'
_IOC_READ = 2L # Variable c_uint '2u'
_LARGEFILE64_SOURCE = 1 # Variable c_int '1'
_IO_MAGIC_MASK = 4294901760L # Variable c_uint '4294901760u'
__USE_XOPEN2K8 = 1 # Variable c_int '1'
_STRUCT_TIMEVAL = 1 # Variable c_int '1'
SIOCGIFHWADDR = 35111 # Variable c_int '35111'
COMEDI_EV_CONVERT = 1048576 # Variable c_int '1048576'
SIOCSIFMETRIC = 35102 # Variable c_int '35102'
SIOCRTMSG = 35085 # Variable c_int '35085'
P_tmpdir = '/tmp' # Variable STRING '(const char*)"/tmp"'
TRIG_CONFIG = 16 # Variable c_int '16'
TIOCVHANGUP = 21559 # Variable c_int '21559'
IOC_INOUT = 3221225472L # Variable c_uint '3221225472u'
F_NOTIFY = 1026 # Variable c_int '1026'
TIOCPKT_DATA = 0 # Variable c_int '0'
_BITS_PTHREADTYPES_H = 1 # Variable c_int '1'
_IO_FLAGS2_NOTCANCEL = 2 # Variable c_int '2'
FD_CLOEXEC = 1 # Variable c_int '1'
TIOCGPTN = 2147767344L # Variable c_ulong '2147767344ul'
AREF_DIFF = 2 # Variable c_int '2'
SIOCGIFMETRIC = 35101 # Variable c_int '35101'
S_IRGRP = 32 # Variable c_int '32'
TIOCCBRK = 21544 # Variable c_int '21544'
TIOCLINUX = 21532 # Variable c_int '21532'
TIOCGRS485 = 21550 # Variable c_int '21550'
TRIG_ANY = 4294967295L # Variable c_uint '4294967295u'
_ISOC95_SOURCE = 1 # Variable c_int '1'
_ISOC99_SOURCE = 1 # Variable c_int '1'
TRIG_INT = 128 # Variable c_int '128'
SIOCGIFCONF = 35090 # Variable c_int '35090'
_IOC_SIZEBITS = 14 # Variable c_int '14'
SIOCGIFADDR = 35093 # Variable c_int '35093'
_BITS_STAT_H = 1 # Variable c_int '1'
COMEDI_BUFCONFIG = 2149606413L # Variable c_ulong '2149606413ul'
__clock_t_defined = 1 # Variable c_int '1'
O_NOCTTY = 256 # Variable c_int '256'
_IO_SHOWPOS = 1024 # Variable c_int '1024'
_STDIO_H = 1 # Variable c_int '1'
IOC_OUT = 2147483648L # Variable c_uint '2147483648u'
_IO_MAGIC = 4222418944L # Variable c_uint '4222418944u'
TIOCSERGETMULTI = 21594 # Variable c_int '21594'
O_ACCMODE = 3 # Variable c_int '3'
COMEDI_LOCK = 25605L # Variable c_uint '25605u'
CTIME = 0 # Variable c_int '0'
F_SETLEASE = 1024 # Variable c_int '1024'
N_PPP = 3 # Variable c_int '3'
TIOCGPKT = 2147767352L # Variable c_ulong '2147767352ul'
__SYSCALL_WORDSIZE = 64 # Variable c_int '64'
TCSETSF = 21508 # Variable c_int '21508'
SDF_CMD = 4096 # Variable c_int '4096'
CINTR = 3 # Variable c_int '3'
GPCT_GET_INT_CLK_FRQ = 128 # Variable c_int '128'
_IO_EOF_SEEN = 16 # Variable c_int '16'
__timer_t_defined = 1 # Variable c_int '1'
TCSETSW = 21507 # Variable c_int '21507'
_IO_FIXED = 4096 # Variable c_int '4096'
POSIX_FADV_NORMAL = 0 # Variable c_int '0'
INSN_BITS = 201326594 # Variable c_int '201326594'
_SVID_SOURCE = 1 # Variable c_int '1'
COMEDI_INSN = 2150130700L # Variable c_ulong '2150130700ul'
_IOFBF = 0 # Variable c_int '0'
INSN_MASK_SPECIAL = 33554432 # Variable c_int '33554432'
SDF_BUSY = 1 # Variable c_int '1'
F_GETFD = 1 # Variable c_int '1'
TIOCGSERIAL = 21534 # Variable c_int '21534'
TCSBRKP = 21541 # Variable c_int '21541'
__USE_BSD = 1 # Variable c_int '1'
F_GETFL = 3 # Variable c_int '3'
COMEDI_DEVINFO = 2159043585L # Variable c_ulong '2159043585ul'
SPLICE_F_MOVE = 1 # Variable c_int '1'
TIOCPKT_START = 8 # Variable c_int '8'
SDF_DIFF = 4194304 # Variable c_int '4194304'
_IO_IN_BACKUP = 256 # Variable c_int '256'
_IOS_NOREPLACE = 64 # Variable c_int '64'
F_SETLK = 6 # Variable c_int '6'
MAX_HANDLE_SZ = 128 # Variable c_int '128'
_SIGSET_H_types = 1 # Variable c_int '1'
_ISOC11_SOURCE = 1 # Variable c_int '1'
____FILE_defined = 1 # Variable c_int '1'
SEEK_CUR = 1 # Variable c_int '1'
SIOCDARP = 35155 # Variable c_int '35155'
TIOCGDEV = 2147767346L # Variable c_ulong '2147767346ul'
__SIZEOF_PTHREAD_MUTEX_T = 40 # Variable c_int '40'
__USE_UNIX98 = 1 # Variable c_int '1'
_IO_STDIO = 16384 # Variable c_int '16384'
COMEDILIB_VERSION_MAJOR = 0 # Variable c_int '0'
SYNC_FILE_RANGE_WAIT_BEFORE = 1 # Variable c_int '1'
_IO_OCT = 32 # Variable c_int '32'
DN_ACCESS = 1 # Variable c_int '1'
POSIX_FADV_WILLNEED = 3 # Variable c_int '3'
SIOCGIFDSTADDR = 35095 # Variable c_int '35095'
_IOS_APPEND = 8 # Variable c_int '8'
TIOCSIG = 1074025526L # Variable c_ulong '1074025526ul'
COMEDI_NDEVCONFOPTS = 32 # Variable c_int '32'
SIOCSARP = 35157 # Variable c_int '35157'
NI_GPCT_COUNTING_DIRECTION_SHIFT = 24 # Variable c_int '24'
SIOCADDMULTI = 35121 # Variable c_int '35121'
TIOCGWINSZ = 21523 # Variable c_int '21523'
X_OK = 1 # Variable c_int '1'
__OFF_T_MATCHES_OFF64_T = 1 # Variable c_int '1'
TIOCGICOUNT = 21597 # Variable c_int '21597'
CR_INVERT = -2147483648 # Variable c_int '-0x00000000080000000'
_IO_UNIFIED_JUMPTABLES = 1 # Variable c_int '1'
SIOCADDDLCI = 35200 # Variable c_int '35200'
CERASE = 127 # Variable c_int '127'
TCSETAW = 21511 # Variable c_int '21511'
F_SHLCK = 8 # Variable c_int '8'
COMEDI_NDEVICES = 16 # Variable c_int '16'
SIOCDELRT = 35084 # Variable c_int '35084'
TCSETAF = 21512 # Variable c_int '21512'
IOC_IN = 1073741824L # Variable c_uint '1073741824u'
CWERASE = 23 # Variable c_int '23'
SIOCSIFNETMASK = 35100 # Variable c_int '35100'
CIO = 'd' # Variable c_char "'d'"
_IO_FLAGS2_USER_WBUF = 8 # Variable c_int '8'
TRIG_ROUND_UP_NEXT = 196608 # Variable c_int '196608'
SIOCDEVPRIVATE = 35312 # Variable c_int '35312'
SIOCDRARP = 35168 # Variable c_int '35168'
LOCK_EX = 2 # Variable c_int '2'
TRIG_EXT = 64 # Variable c_int '64'
COMEDI_CB_EOA = 2 # Variable c_int '2'
COMEDI_EV_SCAN_END = 2097152 # Variable c_int '2097152'
TRIG_ROUND_UP = 131072 # Variable c_int '131072'
N_MASC = 8 # Variable c_int '8'
INSN_MASK_WRITE = 134217728 # Variable c_int '134217728'
COMEDI_CB_EOS = 1 # Variable c_int '1'
FIOASYNC = 21586 # Variable c_int '21586'
__SIZEOF_PTHREAD_RWLOCKATTR_T = 8 # Variable c_int '8'
TIOCM_RTS = 4 # Variable c_int '4'
LOCK_NB = 4 # Variable c_int '4'
AT_EMPTY_PATH = 4096 # Variable c_int '4096'
TIOCSSERIAL = 21535 # Variable c_int '21535'
INSN_INTTRIG = 167772166 # Variable c_int '167772166'
N_X25 = 6 # Variable c_int '6'
COMEDI_POLL = 25615L # Variable c_uint '25615u'
_IOC_NRBITS = 8 # Variable c_int '8'
COMEDI_DEVCONF_AUX_DATA0_LENGTH = 28 # Variable c_int '28'
_SIGSET_NWORDS = 16L # Variable c_ulong '16ul'
TCSBRK = 21513 # Variable c_int '21513'
TIOCGLCKTRMIOS = 21590 # Variable c_int '21590'
DN_MULTISHOT = 2147483648L # Variable c_uint '2147483648u'
TIOCM_CTS = 32 # Variable c_int '32'
SDF_BUSY_OWNER = 2 # Variable c_int '2'
_IO_CURRENTLY_PUTTING = 2048 # Variable c_int '2048'
__USE_ISOC11 = 1 # Variable c_int '1'
F_EXLCK = 4 # Variable c_int '4'
_IOC_DIRBITS = 2 # Variable c_int '2'
IOCSIZE_MASK = 1073676288 # Variable c_int '1073676288'
_IOLBF = 1 # Variable c_int '1'
AT_FDCWD = -100 # Variable c_int '-0x00000000000000064'
lsampl_t = c_uint
sampl_t = c_ushort

# values for enumeration 'comedi_subdevice_type'
comedi_subdevice_type = c_int # enum

# values for enumeration 'configuration_ids'
configuration_ids = c_int # enum

# values for enumeration 'comedi_io_direction'
comedi_io_direction = c_int # enum

# values for enumeration 'comedi_support_level'
comedi_support_level = c_int # enum
class comedi_trig_struct(Structure):
    pass
comedi_trig = comedi_trig_struct
class comedi_cmd_struct(Structure):
    pass
comedi_cmd = comedi_cmd_struct
class comedi_insn_struct(Structure):
    pass
comedi_insn = comedi_insn_struct
class comedi_insnlist_struct(Structure):
    pass
comedi_insnlist = comedi_insnlist_struct
class comedi_chaninfo_struct(Structure):
    pass
comedi_chaninfo = comedi_chaninfo_struct
class comedi_subdinfo_struct(Structure):
    pass
comedi_subdinfo = comedi_subdinfo_struct
class comedi_devinfo_struct(Structure):
    pass
comedi_devinfo = comedi_devinfo_struct
class comedi_devconfig_struct(Structure):
    pass
comedi_devconfig = comedi_devconfig_struct
class comedi_rangeinfo_struct(Structure):
    pass
comedi_rangeinfo = comedi_rangeinfo_struct
class comedi_krange_struct(Structure):
    pass
comedi_krange = comedi_krange_struct
class comedi_bufconfig_struct(Structure):
    pass
comedi_bufconfig = comedi_bufconfig_struct
class comedi_bufinfo_struct(Structure):
    pass
comedi_bufinfo = comedi_bufinfo_struct
comedi_trig_struct._fields_ = [
    ('subdev', c_uint),
    ('mode', c_uint),
    ('flags', c_uint),
    ('n_chan', c_uint),
    ('chanlist', POINTER(c_uint)),
    ('data', POINTER(sampl_t)),
    ('n', c_uint),
    ('trigsrc', c_uint),
    ('trigvar', c_uint),
    ('trigvar1', c_uint),
    ('data_len', c_uint),
    ('unused', c_uint * 3),
]
comedi_insn_struct._fields_ = [
    ('insn', c_uint),
    ('n', c_uint),
    ('data', POINTER(lsampl_t)),
    ('subdev', c_uint),
    ('chanspec', c_uint),
    ('unused', c_uint * 3),
]
comedi_insnlist_struct._fields_ = [
    ('n_insns', c_uint),
    ('insns', POINTER(comedi_insn)),
]
comedi_cmd_struct._fields_ = [
    ('subdev', c_uint),
    ('flags', c_uint),
    ('start_src', c_uint),
    ('start_arg', c_uint),
    ('scan_begin_src', c_uint),
    ('scan_begin_arg', c_uint),
    ('convert_src', c_uint),
    ('convert_arg', c_uint),
    ('scan_end_src', c_uint),
    ('scan_end_arg', c_uint),
    ('stop_src', c_uint),
    ('stop_arg', c_uint),
    ('chanlist', POINTER(c_uint)),
    ('chanlist_len', c_uint),
    ('data', POINTER(sampl_t)),
    ('data_len', c_uint),
]
comedi_chaninfo_struct._fields_ = [
    ('subdev', c_uint),
    ('maxdata_list', POINTER(lsampl_t)),
    ('flaglist', POINTER(c_uint)),
    ('rangelist', POINTER(c_uint)),
    ('unused', c_uint * 4),
]
comedi_rangeinfo_struct._fields_ = [
    ('range_type', c_uint),
    ('range_ptr', c_void_p),
]
comedi_krange_struct._fields_ = [
    ('min', c_int),
    ('max', c_int),
    ('flags', c_uint),
]
comedi_subdinfo_struct._fields_ = [
    ('type', c_uint),
    ('n_chan', c_uint),
    ('subd_flags', c_uint),
    ('timer_type', c_uint),
    ('len_chanlist', c_uint),
    ('maxdata', lsampl_t),
    ('flags', c_uint),
    ('range_type', c_uint),
    ('settling_time_0', c_uint),
    ('insn_bits_support', c_uint),
    ('unused', c_uint * 8),
]
comedi_devinfo_struct._fields_ = [
    ('version_code', c_uint),
    ('n_subdevs', c_uint),
    ('driver_name', c_char * 20),
    ('board_name', c_char * 20),
    ('read_subdevice', c_int),
    ('write_subdevice', c_int),
    ('unused', c_int * 30),
]
comedi_devconfig_struct._fields_ = [
    ('board_name', c_char * 20),
    ('options', c_int * 32),
]
comedi_bufconfig_struct._fields_ = [
    ('subdevice', c_uint),
    ('flags', c_uint),
    ('maximum_size', c_uint),
    ('size', c_uint),
    ('unused', c_uint * 4),
]
comedi_bufinfo_struct._fields_ = [
    ('subdevice', c_uint),
    ('bytes_read', c_uint),
    ('buf_write_ptr', c_uint),
    ('buf_read_ptr', c_uint),
    ('buf_write_count', c_uint),
    ('buf_read_count', c_uint),
    ('bytes_written', c_uint),
    ('unused', c_uint * 4),
]

# values for enumeration 'i8254_mode'
i8254_mode = c_int # enum

# values for enumeration 'ni_gpct_mode_bits'
ni_gpct_mode_bits = c_int # enum

# values for enumeration 'ni_gpct_clock_source_bits'
ni_gpct_clock_source_bits = c_int # enum

# values for enumeration 'ni_gpct_gate_select'
ni_gpct_gate_select = c_int # enum

# values for enumeration 'ni_gpct_other_index'
ni_gpct_other_index = c_int # enum

# values for enumeration 'ni_gpct_other_select'
ni_gpct_other_select = c_int # enum

# values for enumeration 'ni_gpct_arm_source'
ni_gpct_arm_source = c_int # enum

# values for enumeration 'ni_gpct_filter_select'
ni_gpct_filter_select = c_int # enum

# values for enumeration 'ni_pfi_filter_select'
ni_pfi_filter_select = c_int # enum

# values for enumeration 'ni_mio_clock_source'
ni_mio_clock_source = c_int # enum

# values for enumeration 'ni_rtsi_routing'
ni_rtsi_routing = c_int # enum

# values for enumeration 'ni_pfi_routing'
ni_pfi_routing = c_int # enum

# values for enumeration 'ni_660x_pfi_routing'
ni_660x_pfi_routing = c_int # enum

# values for enumeration 'comedi_counter_status_flags'
comedi_counter_status_flags = c_int # enum

# values for enumeration 'ni_m_series_cdio_scan_begin_src'
ni_m_series_cdio_scan_begin_src = c_int # enum

# values for enumeration 'ni_freq_out_clock_source_bits'
ni_freq_out_clock_source_bits = c_int # enum

# values for enumeration 'amplc_dio_clock_source'
amplc_dio_clock_source = c_int # enum

# values for enumeration 'amplc_dio_gate_source'
amplc_dio_gate_source = c_int # enum
class comedi_t_struct(Structure):
    pass
comedi_t = comedi_t_struct
comedi_t_struct._fields_ = [
]
class comedi_range(Structure):
    pass
comedi_range._fields_ = [
    ('min', c_double),
    ('max', c_double),
    ('unit', c_uint),
]
class comedi_sv_struct(Structure):
    pass
comedi_sv_struct._fields_ = [
    ('dev', POINTER(comedi_t)),
    ('subdevice', c_uint),
    ('chan', c_uint),
    ('range', c_int),
    ('aref', c_int),
    ('n', c_int),
    ('maxdata', lsampl_t),
]
comedi_sv_t = comedi_sv_struct

# values for enumeration 'comedi_oor_behavior'
comedi_oor_behavior = c_int # enum
comedi_open = _libraries['libcomedi.so.0'].comedi_open
comedi_open.restype = POINTER(comedi_t)
comedi_open.argtypes = [STRING]
comedi_close = _libraries['libcomedi.so.0'].comedi_close
comedi_close.restype = c_int
comedi_close.argtypes = [POINTER(comedi_t)]
comedi_loglevel = _libraries['libcomedi.so.0'].comedi_loglevel
comedi_loglevel.restype = c_int
comedi_loglevel.argtypes = [c_int]
comedi_perror = _libraries['libcomedi.so.0'].comedi_perror
comedi_perror.restype = None
comedi_perror.argtypes = [STRING]
comedi_strerror = _libraries['libcomedi.so.0'].comedi_strerror
comedi_strerror.restype = STRING
comedi_strerror.argtypes = [c_int]
comedi_errno = _libraries['libcomedi.so.0'].comedi_errno
comedi_errno.restype = c_int
comedi_errno.argtypes = []
comedi_fileno = _libraries['libcomedi.so.0'].comedi_fileno
comedi_fileno.restype = c_int
comedi_fileno.argtypes = [POINTER(comedi_t)]
comedi_set_global_oor_behavior = _libraries['libcomedi.so.0'].comedi_set_global_oor_behavior
comedi_set_global_oor_behavior.restype = comedi_oor_behavior
comedi_set_global_oor_behavior.argtypes = [comedi_oor_behavior]
comedi_get_n_subdevices = _libraries['libcomedi.so.0'].comedi_get_n_subdevices
comedi_get_n_subdevices.restype = c_int
comedi_get_n_subdevices.argtypes = [POINTER(comedi_t)]
comedi_get_version_code = _libraries['libcomedi.so.0'].comedi_get_version_code
comedi_get_version_code.restype = c_int
comedi_get_version_code.argtypes = [POINTER(comedi_t)]
comedi_get_driver_name = _libraries['libcomedi.so.0'].comedi_get_driver_name
comedi_get_driver_name.restype = STRING
comedi_get_driver_name.argtypes = [POINTER(comedi_t)]
comedi_get_board_name = _libraries['libcomedi.so.0'].comedi_get_board_name
comedi_get_board_name.restype = STRING
comedi_get_board_name.argtypes = [POINTER(comedi_t)]
comedi_get_read_subdevice = _libraries['libcomedi.so.0'].comedi_get_read_subdevice
comedi_get_read_subdevice.restype = c_int
comedi_get_read_subdevice.argtypes = [POINTER(comedi_t)]
comedi_get_write_subdevice = _libraries['libcomedi.so.0'].comedi_get_write_subdevice
comedi_get_write_subdevice.restype = c_int
comedi_get_write_subdevice.argtypes = [POINTER(comedi_t)]
comedi_get_subdevice_type = _libraries['libcomedi.so.0'].comedi_get_subdevice_type
comedi_get_subdevice_type.restype = c_int
comedi_get_subdevice_type.argtypes = [POINTER(comedi_t), c_uint]
comedi_find_subdevice_by_type = _libraries['libcomedi.so.0'].comedi_find_subdevice_by_type
comedi_find_subdevice_by_type.restype = c_int
comedi_find_subdevice_by_type.argtypes = [POINTER(comedi_t), c_int, c_uint]
comedi_get_subdevice_flags = _libraries['libcomedi.so.0'].comedi_get_subdevice_flags
comedi_get_subdevice_flags.restype = c_int
comedi_get_subdevice_flags.argtypes = [POINTER(comedi_t), c_uint]
comedi_get_n_channels = _libraries['libcomedi.so.0'].comedi_get_n_channels
comedi_get_n_channels.restype = c_int
comedi_get_n_channels.argtypes = [POINTER(comedi_t), c_uint]
comedi_range_is_chan_specific = _libraries['libcomedi.so.0'].comedi_range_is_chan_specific
comedi_range_is_chan_specific.restype = c_int
comedi_range_is_chan_specific.argtypes = [POINTER(comedi_t), c_uint]
comedi_maxdata_is_chan_specific = _libraries['libcomedi.so.0'].comedi_maxdata_is_chan_specific
comedi_maxdata_is_chan_specific.restype = c_int
comedi_maxdata_is_chan_specific.argtypes = [POINTER(comedi_t), c_uint]
comedi_get_maxdata = _libraries['libcomedi.so.0'].comedi_get_maxdata
comedi_get_maxdata.restype = lsampl_t
comedi_get_maxdata.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_get_n_ranges = _libraries['libcomedi.so.0'].comedi_get_n_ranges
comedi_get_n_ranges.restype = c_int
comedi_get_n_ranges.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_get_range = _libraries['libcomedi.so.0'].comedi_get_range
comedi_get_range.restype = POINTER(comedi_range)
comedi_get_range.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint]
comedi_find_range = _libraries['libcomedi.so.0'].comedi_find_range
comedi_find_range.restype = c_int
comedi_find_range.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_double, c_double]
comedi_get_buffer_size = _libraries['libcomedi.so.0'].comedi_get_buffer_size
comedi_get_buffer_size.restype = c_int
comedi_get_buffer_size.argtypes = [POINTER(comedi_t), c_uint]
comedi_get_max_buffer_size = _libraries['libcomedi.so.0'].comedi_get_max_buffer_size
comedi_get_max_buffer_size.restype = c_int
comedi_get_max_buffer_size.argtypes = [POINTER(comedi_t), c_uint]
comedi_set_buffer_size = _libraries['libcomedi.so.0'].comedi_set_buffer_size
comedi_set_buffer_size.restype = c_int
comedi_set_buffer_size.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_do_insnlist = _libraries['libcomedi.so.0'].comedi_do_insnlist
comedi_do_insnlist.restype = c_int
comedi_do_insnlist.argtypes = [POINTER(comedi_t), POINTER(comedi_insnlist)]
comedi_do_insn = _libraries['libcomedi.so.0'].comedi_do_insn
comedi_do_insn.restype = c_int
comedi_do_insn.argtypes = [POINTER(comedi_t), POINTER(comedi_insn)]
comedi_lock = _libraries['libcomedi.so.0'].comedi_lock
comedi_lock.restype = c_int
comedi_lock.argtypes = [POINTER(comedi_t), c_uint]
comedi_unlock = _libraries['libcomedi.so.0'].comedi_unlock
comedi_unlock.restype = c_int
comedi_unlock.argtypes = [POINTER(comedi_t), c_uint]
comedi_to_phys = _libraries['libcomedi.so.0'].comedi_to_phys
comedi_to_phys.restype = c_double
comedi_to_phys.argtypes = [lsampl_t, POINTER(comedi_range), lsampl_t]
comedi_from_phys = _libraries['libcomedi.so.0'].comedi_from_phys
comedi_from_phys.restype = lsampl_t
comedi_from_phys.argtypes = [c_double, POINTER(comedi_range), lsampl_t]
comedi_sampl_to_phys = _libraries['libcomedi.so.0'].comedi_sampl_to_phys
comedi_sampl_to_phys.restype = c_int
comedi_sampl_to_phys.argtypes = [POINTER(c_double), c_int, POINTER(sampl_t), c_int, POINTER(comedi_range), lsampl_t, c_int]
comedi_sampl_from_phys = _libraries['libcomedi.so.0'].comedi_sampl_from_phys
comedi_sampl_from_phys.restype = c_int
comedi_sampl_from_phys.argtypes = [POINTER(sampl_t), c_int, POINTER(c_double), c_int, POINTER(comedi_range), lsampl_t, c_int]
comedi_data_read = _libraries['libcomedi.so.0'].comedi_data_read
comedi_data_read.restype = c_int
comedi_data_read.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint, POINTER(lsampl_t)]
comedi_data_read_n = _libraries['libcomedi.so.0'].comedi_data_read_n
comedi_data_read_n.restype = c_int
comedi_data_read_n.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint, POINTER(lsampl_t), c_uint]
comedi_data_read_hint = _libraries['libcomedi.so.0'].comedi_data_read_hint
comedi_data_read_hint.restype = c_int
comedi_data_read_hint.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint]
comedi_data_read_delayed = _libraries['libcomedi.so.0'].comedi_data_read_delayed
comedi_data_read_delayed.restype = c_int
comedi_data_read_delayed.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint, POINTER(lsampl_t), c_uint]
comedi_data_write = _libraries['libcomedi.so.0'].comedi_data_write
comedi_data_write.restype = c_int
comedi_data_write.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint, lsampl_t]
comedi_dio_config = _libraries['libcomedi.so.0'].comedi_dio_config
comedi_dio_config.restype = c_int
comedi_dio_config.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint]
comedi_dio_get_config = _libraries['libcomedi.so.0'].comedi_dio_get_config
comedi_dio_get_config.restype = c_int
comedi_dio_get_config.argtypes = [POINTER(comedi_t), c_uint, c_uint, POINTER(c_uint)]
comedi_dio_read = _libraries['libcomedi.so.0'].comedi_dio_read
comedi_dio_read.restype = c_int
comedi_dio_read.argtypes = [POINTER(comedi_t), c_uint, c_uint, POINTER(c_uint)]
comedi_dio_write = _libraries['libcomedi.so.0'].comedi_dio_write
comedi_dio_write.restype = c_int
comedi_dio_write.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint]
comedi_dio_bitfield2 = _libraries['libcomedi.so.0'].comedi_dio_bitfield2
comedi_dio_bitfield2.restype = c_int
comedi_dio_bitfield2.argtypes = [POINTER(comedi_t), c_uint, c_uint, POINTER(c_uint), c_uint]
comedi_dio_bitfield = _libraries['libcomedi.so.0'].comedi_dio_bitfield
comedi_dio_bitfield.restype = c_int
comedi_dio_bitfield.argtypes = [POINTER(comedi_t), c_uint, c_uint, POINTER(c_uint)]
comedi_sv_init = _libraries['libcomedi.so.0'].comedi_sv_init
comedi_sv_init.restype = c_int
comedi_sv_init.argtypes = [POINTER(comedi_sv_t), POINTER(comedi_t), c_uint, c_uint]
comedi_sv_update = _libraries['libcomedi.so.0'].comedi_sv_update
comedi_sv_update.restype = c_int
comedi_sv_update.argtypes = [POINTER(comedi_sv_t)]
comedi_sv_measure = _libraries['libcomedi.so.0'].comedi_sv_measure
comedi_sv_measure.restype = c_int
comedi_sv_measure.argtypes = [POINTER(comedi_sv_t), POINTER(c_double)]
comedi_get_cmd_src_mask = _libraries['libcomedi.so.0'].comedi_get_cmd_src_mask
comedi_get_cmd_src_mask.restype = c_int
comedi_get_cmd_src_mask.argtypes = [POINTER(comedi_t), c_uint, POINTER(comedi_cmd)]
comedi_get_cmd_generic_timed = _libraries['libcomedi.so.0'].comedi_get_cmd_generic_timed
comedi_get_cmd_generic_timed.restype = c_int
comedi_get_cmd_generic_timed.argtypes = [POINTER(comedi_t), c_uint, POINTER(comedi_cmd), c_uint, c_uint]
comedi_cancel = _libraries['libcomedi.so.0'].comedi_cancel
comedi_cancel.restype = c_int
comedi_cancel.argtypes = [POINTER(comedi_t), c_uint]
comedi_command = _libraries['libcomedi.so.0'].comedi_command
comedi_command.restype = c_int
comedi_command.argtypes = [POINTER(comedi_t), POINTER(comedi_cmd)]
comedi_command_test = _libraries['libcomedi.so.0'].comedi_command_test
comedi_command_test.restype = c_int
comedi_command_test.argtypes = [POINTER(comedi_t), POINTER(comedi_cmd)]
comedi_poll = _libraries['libcomedi.so.0'].comedi_poll
comedi_poll.restype = c_int
comedi_poll.argtypes = [POINTER(comedi_t), c_uint]
comedi_set_max_buffer_size = _libraries['libcomedi.so.0'].comedi_set_max_buffer_size
comedi_set_max_buffer_size.restype = c_int
comedi_set_max_buffer_size.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_get_buffer_contents = _libraries['libcomedi.so.0'].comedi_get_buffer_contents
comedi_get_buffer_contents.restype = c_int
comedi_get_buffer_contents.argtypes = [POINTER(comedi_t), c_uint]
comedi_mark_buffer_read = _libraries['libcomedi.so.0'].comedi_mark_buffer_read
comedi_mark_buffer_read.restype = c_int
comedi_mark_buffer_read.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_mark_buffer_written = _libraries['libcomedi.so.0'].comedi_mark_buffer_written
comedi_mark_buffer_written.restype = c_int
comedi_mark_buffer_written.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_get_buffer_offset = _libraries['libcomedi.so.0'].comedi_get_buffer_offset
comedi_get_buffer_offset.restype = c_int
comedi_get_buffer_offset.argtypes = [POINTER(comedi_t), c_uint]
class comedi_caldac_t(Structure):
    pass
comedi_caldac_t._fields_ = [
    ('subdevice', c_uint),
    ('channel', c_uint),
    ('value', c_uint),
]
class comedi_polynomial_t(Structure):
    pass
comedi_polynomial_t._fields_ = [
    ('coefficients', c_double * 4),
    ('expansion_origin', c_double),
    ('order', c_uint),
]
class comedi_softcal_t(Structure):
    pass
comedi_softcal_t._fields_ = [
    ('to_phys', POINTER(comedi_polynomial_t)),
    ('from_phys', POINTER(comedi_polynomial_t)),
]
class comedi_calibration_setting_t(Structure):
    pass
comedi_calibration_setting_t._fields_ = [
    ('subdevice', c_uint),
    ('channels', POINTER(c_uint)),
    ('num_channels', c_uint),
    ('ranges', POINTER(c_uint)),
    ('num_ranges', c_uint),
    ('arefs', c_uint * 4),
    ('num_arefs', c_uint),
    ('caldacs', POINTER(comedi_caldac_t)),
    ('num_caldacs', c_uint),
    ('soft_calibration', comedi_softcal_t),
]
class comedi_calibration_t(Structure):
    pass
comedi_calibration_t._fields_ = [
    ('driver_name', STRING),
    ('board_name', STRING),
    ('settings', POINTER(comedi_calibration_setting_t)),
    ('num_settings', c_uint),
]
comedi_parse_calibration_file = _libraries['libcomedi.so.0'].comedi_parse_calibration_file
comedi_parse_calibration_file.restype = POINTER(comedi_calibration_t)
comedi_parse_calibration_file.argtypes = [STRING]
comedi_apply_parsed_calibration = _libraries['libcomedi.so.0'].comedi_apply_parsed_calibration
comedi_apply_parsed_calibration.restype = c_int
comedi_apply_parsed_calibration.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint, POINTER(comedi_calibration_t)]
comedi_get_default_calibration_path = _libraries['libcomedi.so.0'].comedi_get_default_calibration_path
comedi_get_default_calibration_path.restype = STRING
comedi_get_default_calibration_path.argtypes = [POINTER(comedi_t)]
comedi_cleanup_calibration = _libraries['libcomedi.so.0'].comedi_cleanup_calibration
comedi_cleanup_calibration.restype = None
comedi_cleanup_calibration.argtypes = [POINTER(comedi_calibration_t)]
comedi_apply_calibration = _libraries['libcomedi.so.0'].comedi_apply_calibration
comedi_apply_calibration.restype = c_int
comedi_apply_calibration.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint, STRING]

# values for enumeration 'comedi_conversion_direction'
comedi_conversion_direction = c_int # enum
comedi_get_softcal_converter = _libraries['libcomedi.so.0'].comedi_get_softcal_converter
comedi_get_softcal_converter.restype = c_int
comedi_get_softcal_converter.argtypes = [c_uint, c_uint, c_uint, comedi_conversion_direction, POINTER(comedi_calibration_t), POINTER(comedi_polynomial_t)]
comedi_get_hardcal_converter = _libraries['libcomedi.so.0'].comedi_get_hardcal_converter
comedi_get_hardcal_converter.restype = c_int
comedi_get_hardcal_converter.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, comedi_conversion_direction, POINTER(comedi_polynomial_t)]
comedi_to_physical = _libraries['libcomedi.so.0'].comedi_to_physical
comedi_to_physical.restype = c_double
comedi_to_physical.argtypes = [lsampl_t, POINTER(comedi_polynomial_t)]
comedi_from_physical = _libraries['libcomedi.so.0'].comedi_from_physical
comedi_from_physical.restype = lsampl_t
comedi_from_physical.argtypes = [c_double, POINTER(comedi_polynomial_t)]
comedi_internal_trigger = _libraries['libcomedi.so.0'].comedi_internal_trigger
comedi_internal_trigger.restype = c_int
comedi_internal_trigger.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_arm = _libraries['libcomedi.so.0'].comedi_arm
comedi_arm.restype = c_int
comedi_arm.argtypes = [POINTER(comedi_t), c_uint, c_uint]
comedi_reset = _libraries['libcomedi.so.0'].comedi_reset
comedi_reset.restype = c_int
comedi_reset.argtypes = [POINTER(comedi_t), c_uint]
comedi_get_clock_source = _libraries['libcomedi.so.0'].comedi_get_clock_source
comedi_get_clock_source.restype = c_int
comedi_get_clock_source.argtypes = [POINTER(comedi_t), c_uint, c_uint, POINTER(c_uint), POINTER(c_uint)]
comedi_get_gate_source = _libraries['libcomedi.so.0'].comedi_get_gate_source
comedi_get_gate_source.restype = c_int
comedi_get_gate_source.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, POINTER(c_uint)]
comedi_get_routing = _libraries['libcomedi.so.0'].comedi_get_routing
comedi_get_routing.restype = c_int
comedi_get_routing.argtypes = [POINTER(comedi_t), c_uint, c_uint, POINTER(c_uint)]
comedi_set_counter_mode = _libraries['libcomedi.so.0'].comedi_set_counter_mode
comedi_set_counter_mode.restype = c_int
comedi_set_counter_mode.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint]
comedi_set_clock_source = _libraries['libcomedi.so.0'].comedi_set_clock_source
comedi_set_clock_source.restype = c_int
comedi_set_clock_source.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint]
comedi_set_filter = _libraries['libcomedi.so.0'].comedi_set_filter
comedi_set_filter.restype = c_int
comedi_set_filter.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint]
comedi_set_gate_source = _libraries['libcomedi.so.0'].comedi_set_gate_source
comedi_set_gate_source.restype = c_int
comedi_set_gate_source.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint]
comedi_set_other_source = _libraries['libcomedi.so.0'].comedi_set_other_source
comedi_set_other_source.restype = c_int
comedi_set_other_source.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint, c_uint]
comedi_set_routing = _libraries['libcomedi.so.0'].comedi_set_routing
comedi_set_routing.restype = c_int
comedi_set_routing.argtypes = [POINTER(comedi_t), c_uint, c_uint, c_uint]
comedi_get_hardware_buffer_size = _libraries['libcomedi.so.0'].comedi_get_hardware_buffer_size
comedi_get_hardware_buffer_size.restype = c_int
comedi_get_hardware_buffer_size.argtypes = [POINTER(comedi_t), c_uint, comedi_io_direction]
fcntl = _libraries['libcomedi.so.0'].fcntl
fcntl.restype = c_int
fcntl.argtypes = [c_int, c_int]
__mode_t = c_uint
mode_t = __mode_t
creat = _libraries['libcomedi.so.0'].creat
creat.restype = c_int
creat.argtypes = [STRING, mode_t]
creat64 = _libraries['libcomedi.so.0'].creat64
creat64.restype = c_int
creat64.argtypes = [STRING, mode_t]
off_t = __off_t
lockf = _libraries['libcomedi.so.0'].lockf
lockf.restype = c_int
lockf.argtypes = [c_int, c_int, off_t]
off64_t = __off64_t
lockf64 = _libraries['libcomedi.so.0'].lockf64
lockf64.restype = c_int
lockf64.argtypes = [c_int, c_int, off64_t]
posix_fadvise = _libraries['libcomedi.so.0'].posix_fadvise
posix_fadvise.restype = c_int
posix_fadvise.argtypes = [c_int, off_t, off_t, c_int]
posix_fadvise64 = _libraries['libcomedi.so.0'].posix_fadvise64
posix_fadvise64.restype = c_int
posix_fadvise64.argtypes = [c_int, off64_t, off64_t, c_int]
posix_fallocate = _libraries['libcomedi.so.0'].posix_fallocate
posix_fallocate.restype = c_int
posix_fallocate.argtypes = [c_int, off_t, off_t]
posix_fallocate64 = _libraries['libcomedi.so.0'].posix_fallocate64
posix_fallocate64.restype = c_int
posix_fallocate64.argtypes = [c_int, off64_t, off64_t]
class _IO_jump_t(Structure):
    pass
_IO_jump_t._fields_ = [
]
_IO_lock_t = None
class _IO_marker(Structure):
    pass
_IO_marker._fields_ = [
    ('_next', POINTER(_IO_marker)),
    ('_sbuf', POINTER(_IO_FILE)),
    ('_pos', c_int),
]

# values for enumeration '__codecvt_result'
__codecvt_result = c_int # enum
_IO_FILE._fields_ = [
    ('_flags', c_int),
    ('_IO_read_ptr', STRING),
    ('_IO_read_end', STRING),
    ('_IO_read_base', STRING),
    ('_IO_write_base', STRING),
    ('_IO_write_ptr', STRING),
    ('_IO_write_end', STRING),
    ('_IO_buf_base', STRING),
    ('_IO_buf_end', STRING),
    ('_IO_save_base', STRING),
    ('_IO_backup_base', STRING),
    ('_IO_save_end', STRING),
    ('_markers', POINTER(_IO_marker)),
    ('_chain', POINTER(_IO_FILE)),
    ('_fileno', c_int),
    ('_flags2', c_int),
    ('_old_offset', __off_t),
    ('_cur_column', c_ushort),
    ('_vtable_offset', c_byte),
    ('_shortbuf', c_char * 1),
    ('_lock', POINTER(_IO_lock_t)),
    ('_offset', __off64_t),
    ('__pad1', c_void_p),
    ('__pad2', c_void_p),
    ('__pad3', c_void_p),
    ('__pad4', c_void_p),
    ('__pad5', size_t),
    ('_mode', c_int),
    ('_unused2', c_char * 20),
]
class _IO_FILE_plus(Structure):
    pass
_IO_FILE_plus._fields_ = [
]
_IO_2_1_stdin_ = (_IO_FILE_plus).in_dll(_libraries['libcomedi.so.0'], '_IO_2_1_stdin_')
_IO_2_1_stdout_ = (_IO_FILE_plus).in_dll(_libraries['libcomedi.so.0'], '_IO_2_1_stdout_')
_IO_2_1_stderr_ = (_IO_FILE_plus).in_dll(_libraries['libcomedi.so.0'], '_IO_2_1_stderr_')
__io_read_fn = CFUNCTYPE(__ssize_t, c_void_p, STRING, size_t)
__io_write_fn = CFUNCTYPE(__ssize_t, c_void_p, STRING, size_t)
__io_seek_fn = CFUNCTYPE(c_int, c_void_p, POINTER(__off64_t), c_int)
__io_close_fn = CFUNCTYPE(c_int, c_void_p)
cookie_read_function_t = __io_read_fn
cookie_write_function_t = __io_write_fn
cookie_seek_function_t = __io_seek_fn
cookie_close_function_t = __io_close_fn
class _IO_cookie_io_functions_t(Structure):
    pass
_IO_cookie_io_functions_t._fields_ = [
    ('read', POINTER(__io_read_fn)),
    ('write', POINTER(__io_write_fn)),
    ('seek', POINTER(__io_seek_fn)),
    ('close', POINTER(__io_close_fn)),
]
cookie_io_functions_t = _IO_cookie_io_functions_t
class _IO_cookie_file(Structure):
    pass
_IO_cookie_file._fields_ = [
]
__underflow = _libraries['libcomedi.so.0'].__underflow
__underflow.restype = c_int
__underflow.argtypes = [POINTER(_IO_FILE)]
__uflow = _libraries['libcomedi.so.0'].__uflow
__uflow.restype = c_int
__uflow.argtypes = [POINTER(_IO_FILE)]
__overflow = _libraries['libcomedi.so.0'].__overflow
__overflow.restype = c_int
__overflow.argtypes = [POINTER(_IO_FILE), c_int]
_IO_getc = _libraries['libcomedi.so.0']._IO_getc
_IO_getc.restype = c_int
_IO_getc.argtypes = [POINTER(_IO_FILE)]
_IO_putc = _libraries['libcomedi.so.0']._IO_putc
_IO_putc.restype = c_int
_IO_putc.argtypes = [c_int, POINTER(_IO_FILE)]
_IO_feof = _libraries['libcomedi.so.0']._IO_feof
_IO_feof.restype = c_int
_IO_feof.argtypes = [POINTER(_IO_FILE)]
_IO_ferror = _libraries['libcomedi.so.0']._IO_ferror
_IO_ferror.restype = c_int
_IO_ferror.argtypes = [POINTER(_IO_FILE)]
_IO_peekc_locked = _libraries['libcomedi.so.0']._IO_peekc_locked
_IO_peekc_locked.restype = c_int
_IO_peekc_locked.argtypes = [POINTER(_IO_FILE)]
_IO_flockfile = _libraries['libcomedi.so.0']._IO_flockfile
_IO_flockfile.restype = None
_IO_flockfile.argtypes = [POINTER(_IO_FILE)]
_IO_funlockfile = _libraries['libcomedi.so.0']._IO_funlockfile
_IO_funlockfile.restype = None
_IO_funlockfile.argtypes = [POINTER(_IO_FILE)]
_IO_ftrylockfile = _libraries['libcomedi.so.0']._IO_ftrylockfile
_IO_ftrylockfile.restype = c_int
_IO_ftrylockfile.argtypes = [POINTER(_IO_FILE)]
_IO_vfscanf = _libraries['libcomedi.so.0']._IO_vfscanf
_IO_vfscanf.restype = c_int
_IO_vfscanf.argtypes = [POINTER(_IO_FILE), STRING, POINTER(__va_list_tag), POINTER(c_int)]
_IO_vfprintf = _libraries['libcomedi.so.0']._IO_vfprintf
_IO_vfprintf.restype = c_int
_IO_vfprintf.argtypes = [POINTER(_IO_FILE), STRING, POINTER(__va_list_tag)]
_IO_padn = _libraries['libcomedi.so.0']._IO_padn
_IO_padn.restype = __ssize_t
_IO_padn.argtypes = [POINTER(_IO_FILE), c_int, __ssize_t]
_IO_sgetn = _libraries['libcomedi.so.0']._IO_sgetn
_IO_sgetn.restype = size_t
_IO_sgetn.argtypes = [POINTER(_IO_FILE), c_void_p, size_t]
_IO_seekoff = _libraries['libcomedi.so.0']._IO_seekoff
_IO_seekoff.restype = __off64_t
_IO_seekoff.argtypes = [POINTER(_IO_FILE), __off64_t, c_int, c_int]
_IO_seekpos = _libraries['libcomedi.so.0']._IO_seekpos
_IO_seekpos.restype = __off64_t
_IO_seekpos.argtypes = [POINTER(_IO_FILE), __off64_t, c_int]
_IO_free_backup_area = _libraries['libcomedi.so.0']._IO_free_backup_area
_IO_free_backup_area.restype = None
_IO_free_backup_area.argtypes = [POINTER(_IO_FILE)]
FILE = _IO_FILE
__FILE = _IO_FILE
va_list = __gnuc_va_list
fpos_t = _G_fpos_t
fpos64_t = _G_fpos64_t
remove = _libraries['libcomedi.so.0'].remove
remove.restype = c_int
remove.argtypes = [STRING]
rename = _libraries['libcomedi.so.0'].rename
rename.restype = c_int
rename.argtypes = [STRING, STRING]
renameat = _libraries['libcomedi.so.0'].renameat
renameat.restype = c_int
renameat.argtypes = [c_int, STRING, c_int, STRING]
tmpfile = _libraries['libcomedi.so.0'].tmpfile
tmpfile.restype = POINTER(FILE)
tmpfile.argtypes = []
tmpfile64 = _libraries['libcomedi.so.0'].tmpfile64
tmpfile64.restype = POINTER(FILE)
tmpfile64.argtypes = []
tmpnam = _libraries['libcomedi.so.0'].tmpnam
tmpnam.restype = STRING
tmpnam.argtypes = [STRING]
tmpnam_r = _libraries['libcomedi.so.0'].tmpnam_r
tmpnam_r.restype = STRING
tmpnam_r.argtypes = [STRING]
tempnam = _libraries['libcomedi.so.0'].tempnam
tempnam.restype = STRING
tempnam.argtypes = [STRING, STRING]
fclose = _libraries['libcomedi.so.0'].fclose
fclose.restype = c_int
fclose.argtypes = [POINTER(FILE)]
fflush = _libraries['libcomedi.so.0'].fflush
fflush.restype = c_int
fflush.argtypes = [POINTER(FILE)]
fflush_unlocked = _libraries['libcomedi.so.0'].fflush_unlocked
fflush_unlocked.restype = c_int
fflush_unlocked.argtypes = [POINTER(FILE)]
fcloseall = _libraries['libcomedi.so.0'].fcloseall
fcloseall.restype = c_int
fcloseall.argtypes = []
fopen = _libraries['libcomedi.so.0'].fopen
fopen.restype = POINTER(FILE)
fopen.argtypes = [STRING, STRING]
freopen = _libraries['libcomedi.so.0'].freopen
freopen.restype = POINTER(FILE)
freopen.argtypes = [STRING, STRING, POINTER(FILE)]
fopen64 = _libraries['libcomedi.so.0'].fopen64
fopen64.restype = POINTER(FILE)
fopen64.argtypes = [STRING, STRING]
freopen64 = _libraries['libcomedi.so.0'].freopen64
freopen64.restype = POINTER(FILE)
freopen64.argtypes = [STRING, STRING, POINTER(FILE)]
fdopen = _libraries['libcomedi.so.0'].fdopen
fdopen.restype = POINTER(FILE)
fdopen.argtypes = [c_int, STRING]
fopencookie = _libraries['libcomedi.so.0'].fopencookie
fopencookie.restype = POINTER(FILE)
fopencookie.argtypes = [c_void_p, STRING, _IO_cookie_io_functions_t]
fmemopen = _libraries['libcomedi.so.0'].fmemopen
fmemopen.restype = POINTER(FILE)
fmemopen.argtypes = [c_void_p, size_t, STRING]
open_memstream = _libraries['libcomedi.so.0'].open_memstream
open_memstream.restype = POINTER(FILE)
open_memstream.argtypes = [POINTER(STRING), POINTER(size_t)]
setbuf = _libraries['libcomedi.so.0'].setbuf
setbuf.restype = None
setbuf.argtypes = [POINTER(FILE), STRING]
setvbuf = _libraries['libcomedi.so.0'].setvbuf
setvbuf.restype = c_int
setvbuf.argtypes = [POINTER(FILE), STRING, c_int, size_t]
setbuffer = _libraries['libcomedi.so.0'].setbuffer
setbuffer.restype = None
setbuffer.argtypes = [POINTER(FILE), STRING, size_t]
setlinebuf = _libraries['libcomedi.so.0'].setlinebuf
setlinebuf.restype = None
setlinebuf.argtypes = [POINTER(FILE)]
fscanf = _libraries['libcomedi.so.0'].fscanf
fscanf.restype = c_int
fscanf.argtypes = [POINTER(FILE), STRING]
scanf = _libraries['libcomedi.so.0'].scanf
scanf.restype = c_int
scanf.argtypes = [STRING]
sscanf = _libraries['libcomedi.so.0'].sscanf
sscanf.restype = c_int
sscanf.argtypes = [STRING, STRING]
vfscanf = _libraries['libcomedi.so.0'].vfscanf
vfscanf.restype = c_int
vfscanf.argtypes = [POINTER(FILE), STRING, POINTER(__va_list_tag)]
vscanf = _libraries['libcomedi.so.0'].vscanf
vscanf.restype = c_int
vscanf.argtypes = [STRING, POINTER(__va_list_tag)]
vsscanf = _libraries['libcomedi.so.0'].vsscanf
vsscanf.restype = c_int
vsscanf.argtypes = [STRING, STRING, POINTER(__va_list_tag)]
fgetc = _libraries['libcomedi.so.0'].fgetc
fgetc.restype = c_int
fgetc.argtypes = [POINTER(FILE)]
getc = _libraries['libcomedi.so.0'].getc
getc.restype = c_int
getc.argtypes = [POINTER(FILE)]
fputc = _libraries['libcomedi.so.0'].fputc
fputc.restype = c_int
fputc.argtypes = [c_int, POINTER(FILE)]
putc = _libraries['libcomedi.so.0'].putc
putc.restype = c_int
putc.argtypes = [c_int, POINTER(FILE)]
getw = _libraries['libcomedi.so.0'].getw
getw.restype = c_int
getw.argtypes = [POINTER(FILE)]
putw = _libraries['libcomedi.so.0'].putw
putw.restype = c_int
putw.argtypes = [c_int, POINTER(FILE)]
gets = _libraries['libcomedi.so.0'].gets
gets.restype = STRING
gets.argtypes = [STRING]
__getdelim = _libraries['libcomedi.so.0'].__getdelim
__getdelim.restype = __ssize_t
__getdelim.argtypes = [POINTER(STRING), POINTER(size_t), c_int, POINTER(FILE)]
getdelim = _libraries['libcomedi.so.0'].getdelim
getdelim.restype = __ssize_t
getdelim.argtypes = [POINTER(STRING), POINTER(size_t), c_int, POINTER(FILE)]
fputs = _libraries['libcomedi.so.0'].fputs
fputs.restype = c_int
fputs.argtypes = [STRING, POINTER(FILE)]
puts = _libraries['libcomedi.so.0'].puts
puts.restype = c_int
puts.argtypes = [STRING]
ungetc = _libraries['libcomedi.so.0'].ungetc
ungetc.restype = c_int
ungetc.argtypes = [c_int, POINTER(FILE)]
fwrite = _libraries['libcomedi.so.0'].fwrite
fwrite.restype = size_t
fwrite.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
fputs_unlocked = _libraries['libcomedi.so.0'].fputs_unlocked
fputs_unlocked.restype = c_int
fputs_unlocked.argtypes = [STRING, POINTER(FILE)]
fwrite_unlocked = _libraries['libcomedi.so.0'].fwrite_unlocked
fwrite_unlocked.restype = size_t
fwrite_unlocked.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
fseek = _libraries['libcomedi.so.0'].fseek
fseek.restype = c_int
fseek.argtypes = [POINTER(FILE), c_long, c_int]
ftell = _libraries['libcomedi.so.0'].ftell
ftell.restype = c_long
ftell.argtypes = [POINTER(FILE)]
rewind = _libraries['libcomedi.so.0'].rewind
rewind.restype = None
rewind.argtypes = [POINTER(FILE)]
fseeko = _libraries['libcomedi.so.0'].fseeko
fseeko.restype = c_int
fseeko.argtypes = [POINTER(FILE), __off_t, c_int]
ftello = _libraries['libcomedi.so.0'].ftello
ftello.restype = __off_t
ftello.argtypes = [POINTER(FILE)]
fgetpos = _libraries['libcomedi.so.0'].fgetpos
fgetpos.restype = c_int
fgetpos.argtypes = [POINTER(FILE), POINTER(fpos_t)]
fsetpos = _libraries['libcomedi.so.0'].fsetpos
fsetpos.restype = c_int
fsetpos.argtypes = [POINTER(FILE), POINTER(fpos_t)]
fseeko64 = _libraries['libcomedi.so.0'].fseeko64
fseeko64.restype = c_int
fseeko64.argtypes = [POINTER(FILE), __off64_t, c_int]
ftello64 = _libraries['libcomedi.so.0'].ftello64
ftello64.restype = __off64_t
ftello64.argtypes = [POINTER(FILE)]
fgetpos64 = _libraries['libcomedi.so.0'].fgetpos64
fgetpos64.restype = c_int
fgetpos64.argtypes = [POINTER(FILE), POINTER(fpos64_t)]
fsetpos64 = _libraries['libcomedi.so.0'].fsetpos64
fsetpos64.restype = c_int
fsetpos64.argtypes = [POINTER(FILE), POINTER(fpos64_t)]
clearerr = _libraries['libcomedi.so.0'].clearerr
clearerr.restype = None
clearerr.argtypes = [POINTER(FILE)]
feof = _libraries['libcomedi.so.0'].feof
feof.restype = c_int
feof.argtypes = [POINTER(FILE)]
ferror = _libraries['libcomedi.so.0'].ferror
ferror.restype = c_int
ferror.argtypes = [POINTER(FILE)]
clearerr_unlocked = _libraries['libcomedi.so.0'].clearerr_unlocked
clearerr_unlocked.restype = None
clearerr_unlocked.argtypes = [POINTER(FILE)]
perror = _libraries['libcomedi.so.0'].perror
perror.restype = None
perror.argtypes = [STRING]
fileno = _libraries['libcomedi.so.0'].fileno
fileno.restype = c_int
fileno.argtypes = [POINTER(FILE)]
fileno_unlocked = _libraries['libcomedi.so.0'].fileno_unlocked
fileno_unlocked.restype = c_int
fileno_unlocked.argtypes = [POINTER(FILE)]
popen = _libraries['libcomedi.so.0'].popen
popen.restype = POINTER(FILE)
popen.argtypes = [STRING, STRING]
pclose = _libraries['libcomedi.so.0'].pclose
pclose.restype = c_int
pclose.argtypes = [POINTER(FILE)]
ctermid = _libraries['libcomedi.so.0'].ctermid
ctermid.restype = STRING
ctermid.argtypes = [STRING]
cuserid = _libraries['libcomedi.so.0'].cuserid
cuserid.restype = STRING
cuserid.argtypes = [STRING]
class obstack(Structure):
    pass
obstack._fields_ = [
]
flockfile = _libraries['libcomedi.so.0'].flockfile
flockfile.restype = None
flockfile.argtypes = [POINTER(FILE)]
ftrylockfile = _libraries['libcomedi.so.0'].ftrylockfile
ftrylockfile.restype = c_int
ftrylockfile.argtypes = [POINTER(FILE)]
funlockfile = _libraries['libcomedi.so.0'].funlockfile
funlockfile.restype = None
funlockfile.argtypes = [POINTER(FILE)]
__clock_t = c_long
clock_t = __clock_t
__time_t = c_long
time_t = __time_t
__clockid_t = c_int
clockid_t = __clockid_t
__timer_t = c_void_p
timer_t = __timer_t
class timespec(Structure):
    pass
__syscall_slong_t = c_long
timespec._fields_ = [
    ('tv_sec', __time_t),
    ('tv_nsec', __syscall_slong_t),
]

# values for enumeration '__pid_type'
__pid_type = c_int # enum
class f_owner_ex(Structure):
    pass
f_owner_ex._fields_ = [
    ('type', __pid_type),
    ('pid', __pid_t),
]
class file_handle(Structure):
    pass
file_handle._fields_ = [
    ('handle_bytes', c_uint),
    ('handle_type', c_int),
    ('f_handle', c_ubyte * 0),
]
ssize_t = __ssize_t
readahead = _libraries['libcomedi.so.0'].readahead
readahead.restype = ssize_t
readahead.argtypes = [c_int, __off64_t, size_t]
sync_file_range = _libraries['libcomedi.so.0'].sync_file_range
sync_file_range.restype = c_int
sync_file_range.argtypes = [c_int, __off64_t, __off64_t, c_uint]
class iovec(Structure):
    pass
iovec._fields_ = [
    ('iov_base', c_void_p),
    ('iov_len', size_t),
]
vmsplice = _libraries['libcomedi.so.0'].vmsplice
vmsplice.restype = ssize_t
vmsplice.argtypes = [c_int, POINTER(iovec), size_t, c_uint]
splice = _libraries['libcomedi.so.0'].splice
splice.restype = ssize_t
splice.argtypes = [c_int, POINTER(__off64_t), c_int, POINTER(__off64_t), size_t, c_uint]
tee = _libraries['libcomedi.so.0'].tee
tee.restype = ssize_t
tee.argtypes = [c_int, c_int, size_t, c_uint]
fallocate = _libraries['libcomedi.so.0'].fallocate
fallocate.restype = c_int
fallocate.argtypes = [c_int, c_int, __off_t, __off_t]
fallocate64 = _libraries['libcomedi.so.0'].fallocate64
fallocate64.restype = c_int
fallocate64.argtypes = [c_int, c_int, __off64_t, __off64_t]
name_to_handle_at = _libraries['libcomedi.so.0'].name_to_handle_at
name_to_handle_at.restype = c_int
name_to_handle_at.argtypes = [c_int, STRING, POINTER(file_handle), POINTER(c_int), c_int]
open_by_handle_at = _libraries['libcomedi.so.0'].open_by_handle_at
open_by_handle_at.restype = c_int
open_by_handle_at.argtypes = [c_int, POINTER(file_handle), c_int]
class flock(Structure):
    pass
flock._fields_ = [
    ('l_type', c_short),
    ('l_whence', c_short),
    ('l_start', __off_t),
    ('l_len', __off_t),
    ('l_pid', __pid_t),
]
class flock64(Structure):
    pass
flock64._fields_ = [
    ('l_type', c_short),
    ('l_whence', c_short),
    ('l_start', __off64_t),
    ('l_len', __off64_t),
    ('l_pid', __pid_t),
]
__open_2 = _libraries['libcomedi.so.0'].__open_2
__open_2.restype = c_int
__open_2.argtypes = [STRING, c_int]
open = _libraries['libcomedi.so.0'].open
open.restype = c_int
open.argtypes = [STRING, c_int]
__open64_2 = _libraries['libcomedi.so.0'].__open64_2
__open64_2.restype = c_int
__open64_2.argtypes = [STRING, c_int]
open64 = _libraries['libcomedi.so.0'].open64
open64.restype = c_int
open64.argtypes = [STRING, c_int]
__openat_2 = _libraries['libcomedi.so.0'].__openat_2
__openat_2.restype = c_int
__openat_2.argtypes = [c_int, STRING, c_int]
openat = _libraries['libcomedi.so.0'].openat
openat.restype = c_int
openat.argtypes = [c_int, STRING, c_int]
__openat64_2 = _libraries['libcomedi.so.0'].__openat64_2
__openat64_2.restype = c_int
__openat64_2.argtypes = [c_int, STRING, c_int]
openat64 = _libraries['libcomedi.so.0'].openat64
openat64.restype = c_int
openat64.argtypes = [c_int, STRING, c_int]
class winsize(Structure):
    pass
winsize._fields_ = [
    ('ws_row', c_ushort),
    ('ws_col', c_ushort),
    ('ws_xpixel', c_ushort),
    ('ws_ypixel', c_ushort),
]
class termio(Structure):
    pass
termio._fields_ = [
    ('c_iflag', c_ushort),
    ('c_oflag', c_ushort),
    ('c_cflag', c_ushort),
    ('c_lflag', c_ushort),
    ('c_line', c_ubyte),
    ('c_cc', c_ubyte * 8),
]
pthread_t = c_ulong
class pthread_attr_t(Union):
    pass
pthread_attr_t._fields_ = [
    ('__size', c_char * 56),
    ('__align', c_long),
]
class __pthread_internal_list(Structure):
    pass
__pthread_internal_list._fields_ = [
    ('__prev', POINTER(__pthread_internal_list)),
    ('__next', POINTER(__pthread_internal_list)),
]
__pthread_list_t = __pthread_internal_list
class __pthread_mutex_s(Structure):
    pass
__pthread_mutex_s._fields_ = [
    ('__lock', c_int),
    ('__count', c_uint),
    ('__owner', c_int),
    ('__nusers', c_uint),
    ('__kind', c_int),
    ('__spins', c_short),
    ('__elision', c_short),
    ('__list', __pthread_list_t),
]
class pthread_mutex_t(Union):
    pass
pthread_mutex_t._fields_ = [
    ('__data', __pthread_mutex_s),
    ('__size', c_char * 40),
    ('__align', c_long),
]
class pthread_mutexattr_t(Union):
    pass
pthread_mutexattr_t._fields_ = [
    ('__size', c_char * 4),
    ('__align', c_int),
]
class N14pthread_cond_t3DOT_6E(Structure):
    pass
N14pthread_cond_t3DOT_6E._fields_ = [
    ('__lock', c_int),
    ('__futex', c_uint),
    ('__total_seq', c_ulonglong),
    ('__wakeup_seq', c_ulonglong),
    ('__woken_seq', c_ulonglong),
    ('__mutex', c_void_p),
    ('__nwaiters', c_uint),
    ('__broadcast_seq', c_uint),
]
class pthread_cond_t(Union):
    pass
pthread_cond_t._fields_ = [
    ('__data', N14pthread_cond_t3DOT_6E),
    ('__size', c_char * 48),
    ('__align', c_longlong),
]
class pthread_condattr_t(Union):
    pass
pthread_condattr_t._fields_ = [
    ('__size', c_char * 4),
    ('__align', c_int),
]
pthread_key_t = c_uint
pthread_once_t = c_int
class N16pthread_rwlock_t3DOT_9E(Structure):
    pass
N16pthread_rwlock_t3DOT_9E._fields_ = [
    ('__lock', c_int),
    ('__nr_readers', c_uint),
    ('__readers_wakeup', c_uint),
    ('__writer_wakeup', c_uint),
    ('__nr_readers_queued', c_uint),
    ('__nr_writers_queued', c_uint),
    ('__writer', c_int),
    ('__shared', c_int),
    ('__pad1', c_ulong),
    ('__pad2', c_ulong),
    ('__flags', c_uint),
]
class pthread_rwlock_t(Union):
    pass
pthread_rwlock_t._fields_ = [
    ('__data', N16pthread_rwlock_t3DOT_9E),
    ('__size', c_char * 56),
    ('__align', c_long),
]
class pthread_rwlockattr_t(Union):
    pass
pthread_rwlockattr_t._fields_ = [
    ('__size', c_char * 8),
    ('__align', c_long),
]
pthread_spinlock_t = c_int
class pthread_barrier_t(Union):
    pass
pthread_barrier_t._fields_ = [
    ('__size', c_char * 32),
    ('__align', c_long),
]
class pthread_barrierattr_t(Union):
    pass
pthread_barrierattr_t._fields_ = [
    ('__size', c_char * 4),
    ('__align', c_int),
]
__fdelt_chk = _libraries['libcomedi.so.0'].__fdelt_chk
__fdelt_chk.restype = c_long
__fdelt_chk.argtypes = [c_long]
__fdelt_warn = _libraries['libcomedi.so.0'].__fdelt_warn
__fdelt_warn.restype = c_long
__fdelt_warn.argtypes = [c_long]
__sig_atomic_t = c_int
class __sigset_t(Structure):
    pass
__sigset_t._fields_ = [
    ('__val', c_ulong * 16),
]
class stat(Structure):
    pass
__dev_t = c_ulong
__ino_t = c_ulong
__nlink_t = c_ulong
__gid_t = c_uint
__blksize_t = c_long
__blkcnt_t = c_long
stat._fields_ = [
    ('st_dev', __dev_t),
    ('st_ino', __ino_t),
    ('st_nlink', __nlink_t),
    ('st_mode', __mode_t),
    ('st_uid', __uid_t),
    ('st_gid', __gid_t),
    ('__pad0', c_int),
    ('st_rdev', __dev_t),
    ('st_size', __off_t),
    ('st_blksize', __blksize_t),
    ('st_blocks', __blkcnt_t),
    ('st_atim', timespec),
    ('st_mtim', timespec),
    ('st_ctim', timespec),
    ('__glibc_reserved', __syscall_slong_t * 3),
]
class stat64(Structure):
    pass
__ino64_t = c_ulong
__blkcnt64_t = c_long
stat64._fields_ = [
    ('st_dev', __dev_t),
    ('st_ino', __ino64_t),
    ('st_nlink', __nlink_t),
    ('st_mode', __mode_t),
    ('st_uid', __uid_t),
    ('st_gid', __gid_t),
    ('__pad0', c_int),
    ('st_rdev', __dev_t),
    ('st_size', __off_t),
    ('st_blksize', __blksize_t),
    ('st_blocks', __blkcnt64_t),
    ('st_atim', timespec),
    ('st_mtim', timespec),
    ('st_ctim', timespec),
    ('__glibc_reserved', __syscall_slong_t * 3),
]
getchar = _libraries['libcomedi.so.0'].getchar
getchar.restype = c_int
getchar.argtypes = []
fgetc_unlocked = _libraries['libcomedi.so.0'].fgetc_unlocked
fgetc_unlocked.restype = c_int
fgetc_unlocked.argtypes = [POINTER(FILE)]
getc_unlocked = _libraries['libcomedi.so.0'].getc_unlocked
getc_unlocked.restype = c_int
getc_unlocked.argtypes = [POINTER(FILE)]
getchar_unlocked = _libraries['libcomedi.so.0'].getchar_unlocked
getchar_unlocked.restype = c_int
getchar_unlocked.argtypes = []
putchar = _libraries['libcomedi.so.0'].putchar
putchar.restype = c_int
putchar.argtypes = [c_int]
fputc_unlocked = _libraries['libcomedi.so.0'].fputc_unlocked
fputc_unlocked.restype = c_int
fputc_unlocked.argtypes = [c_int, POINTER(FILE)]
putc_unlocked = _libraries['libcomedi.so.0'].putc_unlocked
putc_unlocked.restype = c_int
putc_unlocked.argtypes = [c_int, POINTER(FILE)]
putchar_unlocked = _libraries['libcomedi.so.0'].putchar_unlocked
putchar_unlocked.restype = c_int
putchar_unlocked.argtypes = [c_int]
getline = _libraries['libcomedi.so.0'].getline
getline.restype = __ssize_t
getline.argtypes = [POINTER(STRING), POINTER(size_t), POINTER(FILE)]
feof_unlocked = _libraries['libcomedi.so.0'].feof_unlocked
feof_unlocked.restype = c_int
feof_unlocked.argtypes = [POINTER(FILE)]
ferror_unlocked = _libraries['libcomedi.so.0'].ferror_unlocked
ferror_unlocked.restype = c_int
ferror_unlocked.argtypes = [POINTER(FILE)]
__sprintf_chk = _libraries['libcomedi.so.0'].__sprintf_chk
__sprintf_chk.restype = c_int
__sprintf_chk.argtypes = [STRING, c_int, size_t, STRING]
__vsprintf_chk = _libraries['libcomedi.so.0'].__vsprintf_chk
__vsprintf_chk.restype = c_int
__vsprintf_chk.argtypes = [STRING, c_int, size_t, STRING, POINTER(__va_list_tag)]
sprintf = _libraries['libcomedi.so.0'].sprintf
sprintf.restype = c_int
sprintf.argtypes = [STRING, STRING]
vsprintf = _libraries['libcomedi.so.0'].vsprintf
vsprintf.restype = c_int
vsprintf.argtypes = [STRING, STRING, POINTER(__va_list_tag)]
__snprintf_chk = _libraries['libcomedi.so.0'].__snprintf_chk
__snprintf_chk.restype = c_int
__snprintf_chk.argtypes = [STRING, size_t, c_int, size_t, STRING]
__vsnprintf_chk = _libraries['libcomedi.so.0'].__vsnprintf_chk
__vsnprintf_chk.restype = c_int
__vsnprintf_chk.argtypes = [STRING, size_t, c_int, size_t, STRING, POINTER(__va_list_tag)]
snprintf = _libraries['libcomedi.so.0'].snprintf
snprintf.restype = c_int
snprintf.argtypes = [STRING, size_t, STRING]
vsnprintf = _libraries['libcomedi.so.0'].vsnprintf
vsnprintf.restype = c_int
vsnprintf.argtypes = [STRING, size_t, STRING, POINTER(__va_list_tag)]
__fprintf_chk = _libraries['libcomedi.so.0'].__fprintf_chk
__fprintf_chk.restype = c_int
__fprintf_chk.argtypes = [POINTER(FILE), c_int, STRING]
__printf_chk = _libraries['libcomedi.so.0'].__printf_chk
__printf_chk.restype = c_int
__printf_chk.argtypes = [c_int, STRING]
__vfprintf_chk = _libraries['libcomedi.so.0'].__vfprintf_chk
__vfprintf_chk.restype = c_int
__vfprintf_chk.argtypes = [POINTER(FILE), c_int, STRING, POINTER(__va_list_tag)]
__vprintf_chk = _libraries['libcomedi.so.0'].__vprintf_chk
__vprintf_chk.restype = c_int
__vprintf_chk.argtypes = [c_int, STRING, POINTER(__va_list_tag)]
fprintf = _libraries['libcomedi.so.0'].fprintf
fprintf.restype = c_int
fprintf.argtypes = [POINTER(FILE), STRING]
printf = _libraries['libcomedi.so.0'].printf
printf.restype = c_int
printf.argtypes = [STRING]
vprintf = _libraries['libcomedi.so.0'].vprintf
vprintf.restype = c_int
vprintf.argtypes = [STRING, POINTER(__va_list_tag)]
vfprintf = _libraries['libcomedi.so.0'].vfprintf
vfprintf.restype = c_int
vfprintf.argtypes = [POINTER(FILE), STRING, POINTER(__va_list_tag)]
__dprintf_chk = _libraries['libcomedi.so.0'].__dprintf_chk
__dprintf_chk.restype = c_int
__dprintf_chk.argtypes = [c_int, c_int, STRING]
__vdprintf_chk = _libraries['libcomedi.so.0'].__vdprintf_chk
__vdprintf_chk.restype = c_int
__vdprintf_chk.argtypes = [c_int, c_int, STRING, POINTER(__va_list_tag)]
dprintf = _libraries['libcomedi.so.0'].dprintf
dprintf.restype = c_int
dprintf.argtypes = [c_int, STRING]
vdprintf = _libraries['libcomedi.so.0'].vdprintf
vdprintf.restype = c_int
vdprintf.argtypes = [c_int, STRING, POINTER(__va_list_tag)]
__asprintf_chk = _libraries['libcomedi.so.0'].__asprintf_chk
__asprintf_chk.restype = c_int
__asprintf_chk.argtypes = [POINTER(STRING), c_int, STRING]
__vasprintf_chk = _libraries['libcomedi.so.0'].__vasprintf_chk
__vasprintf_chk.restype = c_int
__vasprintf_chk.argtypes = [POINTER(STRING), c_int, STRING, POINTER(__va_list_tag)]
__obstack_printf_chk = _libraries['libcomedi.so.0'].__obstack_printf_chk
__obstack_printf_chk.restype = c_int
__obstack_printf_chk.argtypes = [POINTER(obstack), c_int, STRING]
__obstack_vprintf_chk = _libraries['libcomedi.so.0'].__obstack_vprintf_chk
__obstack_vprintf_chk.restype = c_int
__obstack_vprintf_chk.argtypes = [POINTER(obstack), c_int, STRING, POINTER(__va_list_tag)]
asprintf = _libraries['libcomedi.so.0'].asprintf
asprintf.restype = c_int
asprintf.argtypes = [POINTER(STRING), STRING]
__asprintf = _libraries['libcomedi.so.0'].__asprintf
__asprintf.restype = c_int
__asprintf.argtypes = [POINTER(STRING), STRING]
obstack_printf = _libraries['libcomedi.so.0'].obstack_printf
obstack_printf.restype = c_int
obstack_printf.argtypes = [POINTER(obstack), STRING]
vasprintf = _libraries['libcomedi.so.0'].vasprintf
vasprintf.restype = c_int
vasprintf.argtypes = [POINTER(STRING), STRING, POINTER(__va_list_tag)]
obstack_vprintf = _libraries['libcomedi.so.0'].obstack_vprintf
obstack_vprintf.restype = c_int
obstack_vprintf.argtypes = [POINTER(obstack), STRING, POINTER(__va_list_tag)]
__fgets_chk = _libraries['libcomedi.so.0'].__fgets_chk
__fgets_chk.restype = STRING
__fgets_chk.argtypes = [STRING, size_t, c_int, POINTER(FILE)]
fgets = _libraries['libcomedi.so.0'].fgets
fgets.restype = STRING
fgets.argtypes = [STRING, c_int, POINTER(FILE)]
__fread_chk = _libraries['libcomedi.so.0'].__fread_chk
__fread_chk.restype = size_t
__fread_chk.argtypes = [c_void_p, size_t, size_t, size_t, POINTER(FILE)]
fread = _libraries['libcomedi.so.0'].fread
fread.restype = size_t
fread.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
__fgets_unlocked_chk = _libraries['libcomedi.so.0'].__fgets_unlocked_chk
__fgets_unlocked_chk.restype = STRING
__fgets_unlocked_chk.argtypes = [STRING, size_t, c_int, POINTER(FILE)]
fgets_unlocked = _libraries['libcomedi.so.0'].fgets_unlocked
fgets_unlocked.restype = STRING
fgets_unlocked.argtypes = [STRING, c_int, POINTER(FILE)]
__fread_unlocked_chk = _libraries['libcomedi.so.0'].__fread_unlocked_chk
__fread_unlocked_chk.restype = size_t
__fread_unlocked_chk.argtypes = [c_void_p, size_t, size_t, size_t, POINTER(FILE)]
fread_unlocked = _libraries['libcomedi.so.0'].fread_unlocked
fread_unlocked.restype = size_t
fread_unlocked.argtypes = [c_void_p, size_t, size_t, POINTER(FILE)]
sys_nerr = (c_int).in_dll(_libraries['libcomedi.so.0'], 'sys_nerr')
sys_errlist = (STRING * 0).in_dll(_libraries['libcomedi.so.0'], 'sys_errlist')
_sys_nerr = (c_int).in_dll(_libraries['libcomedi.so.0'], '_sys_nerr')
_sys_errlist = (STRING * 0).in_dll(_libraries['libcomedi.so.0'], '_sys_errlist')
class timeval(Structure):
    pass
__suseconds_t = c_long
timeval._fields_ = [
    ('tv_sec', __time_t),
    ('tv_usec', __suseconds_t),
]
__u_char = c_ubyte
__u_short = c_ushort
__u_int = c_uint
__u_long = c_ulong
__int8_t = c_byte
__uint8_t = c_ubyte
__int16_t = c_short
__uint16_t = c_ushort
__int32_t = c_int
__uint32_t = c_uint
__int64_t = c_long
__uint64_t = c_ulong
__quad_t = c_long
__u_quad_t = c_ulong
class __fsid_t(Structure):
    pass
__fsid_t._fields_ = [
    ('__val', c_int * 2),
]
__rlim_t = c_ulong
__rlim64_t = c_ulong
__id_t = c_uint
__useconds_t = c_uint
__daddr_t = c_int
__key_t = c_int
__fsblkcnt_t = c_ulong
__fsblkcnt64_t = c_ulong
__fsfilcnt_t = c_ulong
__fsfilcnt64_t = c_ulong
__fsword_t = c_long
__syscall_ulong_t = c_ulong
__loff_t = __off64_t
__qaddr_t = POINTER(__quad_t)
__caddr_t = STRING
__intptr_t = c_long
__socklen_t = c_uint
ioctl = _libraries['libcomedi.so.0'].ioctl
ioctl.restype = c_int
ioctl.argtypes = [c_int, c_ulong]
sigset_t = __sigset_t
__fd_mask = c_long
class fd_set(Structure):
    pass
fd_set._fields_ = [
    ('fds_bits', __fd_mask * 16),
]
fd_mask = __fd_mask
select = _libraries['libcomedi.so.0'].select
select.restype = c_int
select.argtypes = [c_int, POINTER(fd_set), POINTER(fd_set), POINTER(fd_set), POINTER(timeval)]
pselect = _libraries['libcomedi.so.0'].pselect
pselect.restype = c_int
pselect.argtypes = [c_int, POINTER(fd_set), POINTER(fd_set), POINTER(fd_set), POINTER(timespec), POINTER(__sigset_t)]
gnu_dev_major = _libraries['libcomedi.so.0'].gnu_dev_major
gnu_dev_major.restype = c_uint
gnu_dev_major.argtypes = [c_ulonglong]
gnu_dev_minor = _libraries['libcomedi.so.0'].gnu_dev_minor
gnu_dev_minor.restype = c_uint
gnu_dev_minor.argtypes = [c_ulonglong]
gnu_dev_makedev = _libraries['libcomedi.so.0'].gnu_dev_makedev
gnu_dev_makedev.restype = c_ulonglong
gnu_dev_makedev.argtypes = [c_uint, c_uint]
u_char = __u_char
u_short = __u_short
u_int = __u_int
u_long = __u_long
quad_t = __quad_t
u_quad_t = __u_quad_t
fsid_t = __fsid_t
loff_t = __loff_t
ino_t = __ino_t
ino64_t = __ino64_t
dev_t = __dev_t
gid_t = __gid_t
nlink_t = __nlink_t
uid_t = __uid_t
pid_t = __pid_t
id_t = __id_t
daddr_t = __daddr_t
caddr_t = __caddr_t
key_t = __key_t
useconds_t = __useconds_t
suseconds_t = __suseconds_t
ulong = c_ulong
ushort = c_ushort
uint = c_uint
int8_t = c_int8
int16_t = c_int16
int32_t = c_int32
int64_t = c_int64
u_int8_t = c_ubyte
u_int16_t = c_ushort
u_int32_t = c_uint
u_int64_t = c_ulong
register_t = c_long
blksize_t = __blksize_t
blkcnt_t = __blkcnt_t
fsblkcnt_t = __fsblkcnt_t
fsfilcnt_t = __fsfilcnt_t
blkcnt64_t = __blkcnt64_t
fsblkcnt64_t = __fsblkcnt64_t
fsfilcnt64_t = __fsfilcnt64_t
__all__ = ['name_to_handle_at', '__int16_t', 'ni_gpct_arm_source',
           'getc_unlocked', 'NI_CDIO_SCAN_BEGIN_SRC_G0_OUT',
           '__off64_t', 'F_UNLCK', '__S_IFIFO',
           'NI_PFI_OUTPUT_CDI_SAMPLE', '__FD_ISSET', '_IO_BUFSIZ',
           '__FILE', '_IO_off64_t', 'SPLICE_F_NONBLOCK',
           'NI_PFI_FILTER_125ns', 'sampl_t', 'gnu_dev_makedev',
           '_DEFAULT_SOURCE', '__va_list_tag', 'SIOCSIFMTU',
           'INSN_MASK_READ', 'TIOCGPTLCK', 'TRIG_ROUND_NEAREST',
           'comedi_sampl_to_phys', 'COMEDI_NAMELEN', '_IO_SHOWBASE',
           '__codecvt_partial', 'SIOCSIFLINK', 'COMEDI_COUNTER_ARMED',
           'CR_FLAGS_MASK', 'be64toh', 'TIOCM_DTR', 'S_IRWXG',
           'TRIG_DITHER', 'S_IRWXO', 'pthread_t', 'S_IRWXU',
           'comedi_range_is_chan_specific',
           'comedi_get_softcal_converter', 'comedi_set_buffer_size',
           'TIOCSCTTY', 'NI_GPCT_LOADING_ON_GATE_BIT', '_IO_DEC',
           'comedi_set_other_source', 'printf',
           'NI_GPCT_EDGE_GATE_STOPS_STARTS_BITS', 'getchar',
           '_IO_ERR_SEEN', 'fputs_unlocked',
           'INSN_CONFIG_GET_GATE_SRC', 'O_WRONLY',
           'comedi_parse_calibration_file', '__S_IFLNK', 'ftello64',
           'O_PATH', 'NI_GPCT_NEXT_OUT_GATE_SELECT', 'SIOCGIFSLAVE',
           'comedi_fileno', 'comedi_errno', '__S_IFDIR',
           'RF_EXTERNAL', '_IOC_NRMASK', '_IO_FILE', '_IO_BOOLALPHA',
           'NI_RTSI_OUTPUT_RGOUT0', 'AMPLC_DIO_CLK_1KHZ', 'off_t',
           'NI_GPCT_COUNTING_MODE_QUADRATURE_X4_BITS', '__fsblkcnt_t',
           '_STAT_VER_LINUX', 'O_CREAT', 'COMEDI_SUBD_DO',
           '__WORDSIZE', 'COMEDI_SUBD_DI', 'rewind',
           'comedi_subdinfo', 'GPCT_SET_SOURCE',
           'NI_GPCT_CLOCK_SRC_SELECT_MASK', '_XOPEN_SOURCE', 'open64',
           'openat', 'S_IFSOCK', '__GLIBC__', 'pthread_rwlockattr_t',
           'posix_fallocate64', 'funlockfile', '__u_int',
           'POSIX_FADV_NOREUSE', 'N_MOUSE', '__S_IFSOCK', '__O_PATH',
           'CR_CHAN', 'comedi_dio_bitfield', '__glibc_likely',
           '_IONBF', 'pthread_mutexattr_t', '_BITS_UIO_H',
           '__S_IFCHR', 'fwrite', 'openat64', 'blkcnt_t',
           'COMEDI_SUBDINFO', '__NFDBITS', 'FAPPEND',
           'COMEDI_EV_STOP', 'u_char', 'uid_t', 'u_int64_t',
           'u_int16_t', 'INSN_WAIT', 'comedi_cmd_struct',
           'TIOCPKT_FLUSHWRITE', 'comedi_set_max_buffer_size',
           'INSN_CONFIG', '__SIZEOF_PTHREAD_MUTEXATTR_T',
           '__openat64_2', 'comedi_support_level',
           'COMEDI_SUBD_MEMORY', '__fsword_t', 'RANGE_OFFSET',
           'INSN_CONFIG_GET_COUNTER_STATUS', 'flock', 'N_HCI',
           'comedi_range', 'TIOCM_DSR',
           'NI_GPCT_NO_HARDWARE_DISARM_BITS', 'posix_fadvise',
           'INSN_CONFIG_SET_COUNTER_MODE',
           'NI_GPCT_OUTPUT_TC_TOGGLE_BITS', 'comedi_get_board_name',
           'sprintf', 'F_SETLKW', 'COMEDI_BUFINFO', 'comedi_strerror',
           'AMPLC_DIO_CLK_1MHZ', 'UNIT_mA', 'comedi_bufinfo_struct',
           'htobe16', 'comedi_to_physical', '__pthread_list_t',
           'SIOCSIFMEM', 'NI_PFI_OUTPUT_AO_START1',
           'NI_PFI_OUTPUT_AO_UPDATE_N', 'configuration_ids',
           '__rlim64_t', 'TRIG_WRITE', 'NI_GPCT_OR_GATE_BIT',
           'NI_GPCT_EDGE_GATE_STARTS_BITS', 'TIOCSERCONFIG',
           'TRIG_COUNT', '__blksize_t', '__uint64_t',
           'AMPLC_DIO_GAT_RESERVED7', 'AMPLC_DIO_GAT_RESERVED6',
           'AMPLC_DIO_GAT_RESERVED5', 'AMPLC_DIO_GAT_RESERVED4',
           '_sys_nerr', 'I8254_MODE1', 'I8254_MODE0', 'I8254_MODE3',
           'I8254_MODE2', 'I8254_MODE5', 'I8254_MODE4', 'ino64_t',
           'dprintf', 'setbuffer', 'FIONBIO', '__blkcnt64_t',
           '_IOC_TYPEBITS', '__vdprintf_chk', '_IO_TIED_PUT_GET',
           'COMEDI_SUBD_DIO', 'COMEDI_DEVCONF_AUX_DATA_LENGTH',
           'SDF_MAXDATA', '_IO_BE', 'INSN_CONFIG_DIO_QUERY',
           '_IOS_INPUT', '_BITS_TYPES_H', 'PDP_ENDIAN',
           'NI_GPCT_LOGIC_LOW_GATE_SELECT', 'iovec', '__rlim_t',
           '__FLOAT_WORD_ORDER', 'TRIG_NONE', '__uint8_t',
           'TIOCSERGWILD', 'CR_AREF', '__u_char', 'TIOCMSET',
           'COMEDI_INPUT', 'TIOCPKT_FLUSHREAD', '_IOS_ATEND',
           'TIOCPKT_DOSTOP', 'AT_REMOVEDIR',
           'NI_GPCT_DISABLED_GATE_SELECT', 'AREF_COMMON', '__key_t',
           'fseeko64', 'dev_t', 'setlinebuf', 'setvbuf',
           'NI_PFI_OUTPUT_G_SRC0', 'NI_PFI_OUTPUT_G_SRC1', 'F_ULOCK',
           '__GNU_LIBRARY__', '_BITS_TYPESIZES_H', 'comedi_get_range',
           'SDF_READABLE', 'TCFLSH', '__underflow', '_IO_2_1_stdin_',
           'fgetpos64', 'lockf64', 'SIOCGIFNAME', 'TIOCPKT_STOP',
           'FNDELAY', 'GPCT_SINGLE_PW', 'comedi_devinfo',
           '____mbstate_t_defined', 'comedi_internal_trigger',
           'CSTOP', 'comedi_find_subdevice_by_type',
           'comedi_set_routing', 'perror', 'F_SETOWN', 'CR_PACK',
           'NI_GPCT_PXI_STAR_TRIGGER_GATE_SELECT', 'CR_DITHER',
           'GPCT_SET_GATE', 'SWIG_OUTPUT', '__fsid_t', 'CMIN',
           'INSN_CONFIG_PWM_SET_H_BRIDGE', 'FIONREAD',
           '__fprintf_chk', 'TIOCM_LE',
           'NI_GPCT_PRESCALE_X8_CLOCK_SRC_BITS', 'fgetpos',
           'AMPLC_DIO_CLK_100KHZ', 'TRIG_RT', '_IO_padn',
           '__O_NOFOLLOW', 'SIOCGIFFLAGS', '__overflow', 'CLNEXT',
           '__uint32_t', '__F_SETSIG', 'FFSYNC', '_IO_FILE_plus',
           '_IO_va_list', 'INSN_CONFIG_TIMER_1',
           'NI_CDIO_SCAN_BEGIN_SRC_G1_OUT', 'SDF_RT',
           'SDF_SOFT_CALIBRATED', 'int32_t', 'off64_t', '__open_2',
           'COMEDI_TRIG', 'comedi_set_gate_source',
           'INSN_CONFIG_SET_ROUTING', 'putw', 'htole64', 'puts',
           'NI_GPCT_TIMEBASE_3_CLOCK_SRC_BITS', 'SIOCSIFBR',
           'fallocate64', 'gnu_dev_major', 'putc', 'ni_pfi_routing',
           '__PTHREAD_MUTEX_HAVE_ELISION', '_IO_HEX',
           'NI_PFI_OUTPUT_AI_CONVERT', '__S_ISVTX', 'COMEDI_POLL',
           'SIOCSRARP', 'UTIME_OMIT', 'FILENAME_MAX', '__suseconds_t',
           'NI_GPCT_OUTPUT_TC_OR_GATE_TOGGLE_BITS',
           'NI_GPCT_INDEX_PHASE_LOW_A_HIGH_B_BITS',
           'comedi_get_cmd_generic_timed', 'COMEDI_CB_EOBUF',
           'LOCK_RW', 'S_IXOTH', '__INO_T_MATCHES_INO64_T',
           'TRIG_TIME', 'u_short', 'COMEDI_SUBD_PROC', 'SDF_COMMON',
           '_IO_marker', 'AREF_GROUND', 'COMEDI_SUPPORTED',
           '__SIZEOF_PTHREAD_ATTR_T', '__S_IWRITE',
           'comedi_get_hardware_buffer_size', '_IO_lock_t',
           '_IO_2_1_stdout_', 'N_SMSBLOCK', 'SIOCSIFTXQLEN',
           'S_IWGRP', 'pthread_mutex_t', 'NI_660X_PFI_OUTPUT_DIO',
           'fseek', '__USE_XOPEN2KXSI', 'CDISCARD', 'CR_DEGLITCH',
           '__O_DIRECT', 'pthread_condattr_t', 'pthread_once_t',
           '__timer_t', 'amplc_dio_gate_source', 'comedi_sv_init',
           '__USE_XOPEN2K8', 'COMEDI_OOR_NUMBER',
           'NI_GPCT_SOURCE_ENCODER_Z', 'NI_GPCT_SOURCE_ENCODER_B',
           'NI_GPCT_SOURCE_ENCODER_A', 'loff_t', 'TRIG_CONFIG',
           'blksize_t', 'IOC_INOUT', '__F_SETOWN', 'gnu_dev_minor',
           'TIOCGRS485', '_ISOC99_SOURCE', 'AMPLC_DIO_CLK_CLKN',
           'freopen', 'TRIG_INT', 'fread_unlocked', '_IO_MAGIC',
           'TIOCSERGETMULTI', 'ctermid', '__id_t', '_IO_feof',
           'TIOCGPKT', '__timer_t_defined', '_IO_FIXED', 'INSN_BITS',
           'FD_ISSET', '__codecvt_result', '__vasprintf_chk',
           'fcloseall', 'comedi_sv_update', 'comedi_arm',
           '_IO_IN_BACKUP', 'F_SETLK', 'O_DSYNC', '_SIGSET_H_types',
           'N16pthread_rwlock_t3DOT_9E', '__fdelt_chk', 'SIOCDARP',
           'INSN_GTOD', 'NI_MIO_PLL_PXI10_CLOCK', 'SIOCGIFADDR',
           '_IOWR', 'LOCK_SH', 'COMEDI_OPENDRAIN', 'htobe32',
           'BUFSIZ', 'TIOCGICOUNT', 'comedi_to_phys',
           '_IO_UNIFIED_JUMPTABLES', 'comedi_subdevice_type', 'minor',
           'ftello', 'comedi_apply_parsed_calibration',
           'comedi_bufconfig', 'LOCK_EX', 'BYTE_ORDER',
           'COMEDI_CB_EOA', 'O_ACCMODE', 'COMEDI_CB_EOS',
           '__SIZEOF_PTHREAD_RWLOCKATTR_T', '__u_quad_t', 'TIOCM_RTS',
           '__USE_FORTIFY_LEVEL', 'F_OWNER_PID',
           'comedi_get_gate_source', 'INSN_INTTRIG',
           '_LARGEFILE64_SOURCE', 'CTIME', 'TIOCGLCKTRMIOS',
           'useconds_t', 'DN_MULTISHOT', '__O_LARGEFILE',
           'comedi_do_insn', '__USE_ISOC11', 'comedi_devconfig',
           'comedi_reset', 'COMEDI_SUBD_CALIB', 'EOF', 'DN_ATTRIB',
           'freopen64', 'comedi_data_read_hint',
           'comedi_devconfig_struct', 'N11__mbstate_t4DOT_14E',
           'S_IFDIR', 'AMPLC_DIO_CLK_OUTNM1', 'F_GETSIG',
           'SIOCSIFFLAGS', '_IO_fpos64_t', 'COMEDI_FROM_PHYSICAL',
           'comedi_command', 'F_DUPFD_CLOEXEC', '__time_t_defined',
           '__time_t', 'NI_GPCT_COUNTING_DIRECTION_DOWN_BITS',
           '__GLIBC_PREREQ', 'F_DUPFD', '__F_GETOWN',
           'GPCT_SINGLE_PULSE_OUT', 'pthread_rwlock_t',
           'comedi_dio_read', 'timespec', 'SDF_GROUND',
           'TIOCSERGETLSR', 'UTIME_NOW', 'AMPLC_DIO_CLK_10MHZ',
           'GPCT_INT_CLOCK', 'getchar_unlocked', 'COMEDI_CB_OVERFLOW',
           '_G_HAVE_MMAP', 'va_list', '__attribute_format_strfmon__',
           'NI_GPCT_GATE_PIN_i_GATE_SELECT', 'SWIG_INPUT',
           'open_memstream', 'splice', 'fsetpos64', '__u_long',
           'O_DIRECTORY', '__S_ISUID', 'S_IFMT',
           'comedi_get_read_subdevice', 'GPCT_HWUD', 'COMEDI_SUBD_AO',
           'COMEDI_SUBD_AI', 'comedi_set_clock_source',
           '_LARGEFILE_SOURCE', 'O_RSYNC', 'CR_ALT_SOURCE',
           'NI_RTSI_OUTPUT_G_GATE0', '__off_t', 'N_IRDA',
           'NI_GPCT_PRESCALE_MODE_CLOCK_SRC_MASK', 'u_quad_t',
           'SDF_CMD_WRITE', 'SIOCDELDLCI', '_IOS_TRUNC',
           '__F_GETOWN_EX', 'fallocate',
           'NI_GPCT_PXI10_CLOCK_SRC_BITS', 'SIOCSIFDSTADDR',
           '__int8_t', 'comedi_chaninfo', 'CR_EDGE',
           'NI_GPCT_INDEX_PHASE_HIGH_A_LOW_B_BITS', 'CFLUSH',
           'COMEDI_DEVCONFIG', 'ftrylockfile', '_IO_pid_t', 'winsize',
           'pthread_key_t', 'NI_RTSI_OUTPUT_DACUPDN', 'F_GETLK64',
           'comedi_sampl_from_phys', 'u_int8_t', 'N_TTY', 'lockf',
           '_IO_UNITBUF', 'FD_ZERO', 'SIOCGIFCOUNT', 'feof',
           'NI_GPCT_FILTER_10x_TIMEBASE_1',
           'NI_GPCT_INDEX_ENABLE_BIT', 'clearerr',
           'comedi_get_hardcal_converter', 'SDF_LOCK_OWNER',
           'NI_GPCT_UP_DOWN_PIN_i_GATE_SELECT', 'AT_NO_AUTOMOUNT',
           '__S_IREAD', 'GPCT_UP', 'flockfile',
           'NI_GPCT_FILTER_100x_TIMEBASE_1', '__RANGE', 'comedi_poll',
           'COMEDI_DEVCONF_AUX_DATA_HI', 'ioctl', 'uint', 'stdin',
           'CSTART', 'flock64', 'INSN_CONFIG_PWM_GET_PERIOD', 'NCC',
           '__open64_2', 'SDF_DITHER', 'FILE', 'size_t',
           'comedi_insn', 'NI_GPCT_ARM_UNKNOWN', 'F_SETLKW64',
           'ni_gpct_other_select', 'comedi_data_read', '__qaddr_t',
           'comedi_insnlist_struct',
           'NI_GPCT_TIMEBASE_1_CLOCK_SRC_BITS', 'CMDF_WRITE',
           'NI_GPCT_AI_START2_GATE_SELECT', 'cookie_write_function_t',
           '__vprintf_chk', 'sigset_t', 'getdelim', '_IOC_SIZE',
           'comedi_sv_measure', '__USE_POSIX', 'O_NOFOLLOW',
           '__fd_mask', '__useconds_t', '__clockid_t_defined',
           'comedi_apply_calibration', 'TIOCGSID', 'TRIG_INVALID',
           'u_int32_t', 'asprintf', 'ferror',
           '__WORDSIZE_TIME64_COMPAT32', '_IO_cookie_io_functions_t',
           '_SYS_TYPES_H', 'DN_RENAME', '__P',
           'NI_PFI_OUTPUT_FREQ_OUT', '_IOC_TYPEMASK',
           'INSN_CONFIG_SET_GATE_SRC', '__uflow', '__USE_GNU',
           'COMEDI_OUTPUT', 'FALLOC_FL_PUNCH_HOLE',
           'NI_CDIO_SCAN_BEGIN_SRC_AI_START', 'F_RDLCK',
           'pthread_attr_t', '__attribute_format_arg__',
           'NI_GPCT_RELOAD_SOURCE_FIXED_BITS', 'N_STRIP',
           'NI_CDIO_SCAN_BEGIN_SRC_AO_UPDATE',
           'INSN_CONFIG_GET_ROUTING', 'TRIG_TIMER', 'GPCT_EXT_PIN',
           'open', 'NI_CDIO_SCAN_BEGIN_SRC_DIO_CHANGE_DETECT_IRQ',
           'le16toh', '__mbstate_t', '_IO_INTERNAL',
           'NI_GPCT_DISABLED_OTHER_SELECT', 'comedi_oor_behavior',
           'NI_CDIO_SCAN_BEGIN_SRC_GROUND',
           'NI_GPCT_RELOAD_SOURCE_MASK', 'quad_t',
           'INSN_CONFIG_DIO_INPUT', 'SIOCSIFHWADDR', 'pthread_cond_t',
           'comedi_set_counter_mode', 'SIOCSIFENCAP', 'TIOCSERSWILD',
           'SIOCSIFMAP', 'TIOCSWINSZ', 'comedi_cleanup_calibration',
           'nlink_t', 'COMEDI_INSNLIST', '__warnattr',
           'SIOCGIFTXQLEN', 'LOCK_UN', 'ni_mio_clock_source',
           'DN_CREATE', 'SDF_LOCKED', 'ulong', 'comedi_unlock',
           'NI_GPCT_RELOAD_SOURCE_GATE_SELECT_BITS',
           'GPCT_SIMPLE_EVENT', 'int8_t', 'TIOCMIWAIT', 'fsblkcnt_t',
           '__FD_ZERO_STOS', 'vfprintf', '__uint16_t',
           'obstack_vprintf', 'N14pthread_cond_t3DOT_6E', 'FIONCLEX',
           'fsfilcnt_t', 'putchar_unlocked', 'SIOCSIFNAME', 'F_WRLCK',
           'NI_GPCT_COUNTING_MODE_SHIFT', 'AT_SYMLINK_NOFOLLOW',
           '_IOC_TYPE', '_IO_LINE_BUF', 'comedi_t',
           'NI_GPCT_FILTER_2x_TIMEBASE_3',
           'NI_GPCT_FILTER_2x_TIMEBASE_1', 'comedi_devinfo_struct',
           'N_6PACK', 'LOCK_WRITE', '_G_config_h', '_IO_FLAGS2_MMAP',
           'DN_MODIFY', 'comedi_from_phys',
           'INSN_CONFIG_DIGITAL_TRIG', 'fileno',
           'NI_GPCT_COUNTING_MODE_QUADRATURE_X2_BITS',
           'COMEDI_COUNTER_COUNTING', 'comedi_get_subdevice_type',
           'F_GETLK', 'NI_RTSI_OUTPUT_G_SRC0', 'be32toh',
           'NI_PFI_FILTER_OFF', '__openat_2',
           'comedi_get_buffer_size', '_STAT_VER',
           'COMEDI_DEVCONF_AUX_DATA2_LENGTH', '_sys_errlist',
           'NI_GPCT_DISARM_AT_TC_BITS', 'F_LOCK', 'vdprintf',
           'SYNC_FILE_RANGE_WRITE', 'fcntl', '__getdelim',
           '__USE_XOPEN2K', '_IO_LINKED', '__USE_POSIX2',
           '__blkcnt_t', 'SDF_FLAGS', 'blkcnt64_t', '_POSIX_C_SOURCE',
           '__vsnprintf_chk', 'INSN_CONFIG_GPCT_QUADRATURE_ENCODER',
           'NI_GPCT_INDEX_PHASE_HIGH_A_HIGH_B_BITS',
           '__PTHREAD_RWLOCK_INT_FLAGS_SHARED',
           'NI_GPCT_AI_START1_GATE_SELECT', 'INSN_WRITE',
           'TIOCSPTLCK', 'S_IWOTH', 'S_IWUSR', 'clearerr_unlocked',
           'GPCT_SET_DIRECTION', 'NI_RTSI_OUTPUT_RTSI_BRD_0',
           'comedi_krange_struct', 'fread', 'N_SLIP',
           'NI_GPCT_FILTER_20x_TIMEBASE_1', 'SPLICE_F_MORE', 'F_OK',
           '__OFF_T_MATCHES_OFF64_T', 'S_ISVTX', 'comedi_data_write',
           'stdout', 'GPCT_NO_GATE', 'SEEK_HOLE',
           'comedi_subdinfo_struct', '_IOC_DIR', 'time_t',
           'NI_RTSI_OUTPUT_RTSI_OSC', 'FALLOC_FL_KEEP_SIZE',
           'INSN_CONFIG_ARM', 'S_ISUID', 'fsblkcnt64_t', 'TRIG_EXT',
           'NI_MIO_PLL_RTSI0_CLOCK', '_OLD_STDIO_MAGIC',
           '__snprintf_chk', 'TIOCNOTTY', '__vsprintf_chk', 'CBRK',
           'INSN_READ', 'GPCT_DOWN', 'F_OWNER_TID', 'SDF_MMAP',
           '__int64_t', 'COMEDI_EV_SCAN_BEGIN', 'fopen64',
           'SIOCDELMULTI', 'CTRL', '__LITTLE_ENDIAN',
           'COMEDI_SUBD_PWM', '__have_pthread_attr_t',
           'NI_GPCT_STOP_ON_GATE_OR_SECOND_TC_BITS',
           '_STRUCT_TIMEVAL', 'COMEDI_EV_CONVERT', 'SIOCSIFMETRIC',
           'P_tmpdir', 'SDF_MODE1', '__u_short',
           'NI_GPCT_INDEX_PHASE_MASK', '_IO_sgetn', 'F_NOTIFY',
           '_BITS_PTHREADTYPES_H', '_IO_FLAGS2_NOTCANCEL',
           'FD_CLOEXEC', 'TIOCGPTN', 'SIOCGIFMETRIC',
           'NI_GPCT_TIMESTAMP_MUX_GATE_SELECT', 'TIOCCBRK',
           'TRIG_ANY', '__S_IFREG', '__nlink_t', '__syscall_ulong_t',
           'comedi_data_read_delayed', 'O_NOCTTY', 'fgets',
           'comedi_sv_struct', 'cookie_io_functions_t', 'F_SETLEASE',
           '_IOC_NRBITS', 'NI_RTSI_OUTPUT_SCLKG',
           'comedi_maxdata_is_chan_specific',
           'NI_GPCT_HARDWARE_DISARM_MASK', 'ftell',
           'POSIX_FADV_NORMAL', 'comedi_io_direction', '_SVID_SOURCE',
           'INSN_CONFIG_8254_READ_STATUS',
           'NI_GPCT_ANALOG_TRIGGER_OUT_CLOCK_SRC_BITS',
           'NI_GPCT_FILTER_OFF', '_IOFBF', 'SDF_BUSY', 'TCSBRKP',
           'INSN_CONFIG_GPCT_SINGLE_PULSE_GENERATOR',
           'NI_PFI_OUTPUT_CDO_UPDATE', 'MAX_HANDLE_SZ',
           'obstack_printf', '____FILE_defined', '__bos0', 'vsscanf',
           '__SIZEOF_PTHREAD_MUTEX_T', '_IO_STDIO',
           'NI_GPCT_OUTPUT_TC_PULSE_BITS', 'comedi_lock', 'CRPRNT',
           'fdopen', 'ni_gpct_filter_select',
           'SYNC_FILE_RANGE_WAIT_BEFORE', 'POSIX_FADV_WILLNEED',
           '__sig_atomic_t', '__io_seek_fn', 'ni_gpct_gate_select',
           'SIOCADDMULTI', 'X_OK', 'INSN_CONFIG_SET_CLOCK_SRC',
           'TIOCM_CAR', '__S_IFMT',
           'NI_GPCT_NO_PRESCALE_CLOCK_SRC_BITS', '_IO_vfscanf',
           '__socklen_t', 'COMEDI_NDEVICES', 'SIOCDELRT', 'F_GETOWN',
           'fileno_unlocked', 'creat', 'F_TEST', '_IO_2_1_stderr_',
           'NI_GPCT_EDGE_GATE_MODE_MASK', '__STRING',
           'SIOCDEVPRIVATE', 'comedi_calibration_t', '_IO_seekpos',
           'comedi_bufconfig_struct', '__GNUC_PREREQ', 'tmpnam',
           '__PDP_ENDIAN', 'vfscanf', 'TIOCSSERIAL', 'fsid_t',
           '__pid_t', '__va_arg_pack', 'comedi_get_n_channels',
           'INSN_CONFIG_SET_OTHER_SRC', '_SIGSET_NWORDS', 'TCSBRK',
           'comedi_from_physical', '_IOR', 'NI_GPCT_STOP_MODE_MASK',
           'open_by_handle_at', 'F_EXLCK', 'NFDBITS',
           'SDF_PWM_COUNTER', '_IO_USER_LOCK', '_ATFILE_SOURCE',
           'NI_MIO_PLL_PXI_STAR_TRIGGER_CLOCK', 'TRIG_DEGLITCH',
           '_G_HAVE_MREMAP', 'SIOCPROTOPRIVATE', '_IOC', '_G_va_list',
           'makedev', '__O_NOATIME', 'F_GETLEASE', 'htole32',
           'TRIG_NOW', '_POSIX_SOURCE', '_IO_jump_t', 'TIOCM_CD',
           'SIOCADDRT', 'stderr', 'posix_fallocate', 'fputc_unlocked',
           'CEOF', 'CEOL', 'COMEDI_CHANINFO', 'tee', 'CEOT',
           'comedi_get_version_code', 'UNIT_volt',
           'comedi_data_read_n', '_IO_off_t', 'comedi_trig',
           '__clockid_t', 'I8254_BINARY', 'CSTATUS',
           'comedi_trig_struct', '__O_CLOEXEC', 'AMPLC_DIO_GAT_VCC',
           'COMEDI_SUBD_COUNTER', 'comedi_get_subdevice_flags',
           'comedi_set_global_oor_behavior', '_IO_SKIPWS', 'popen',
           '_IO_SCIENTIFIC', '_IOC_SIZEMASK', '_IO_ferror',
           'posix_fadvise64', '__mode_t', 'TIOCSSOFTCAR', 'SIOCDRARP',
           'ni_m_series_cdio_scan_begin_src', 'select',
           'comedi_get_routing', 'comedi_perror',
           'COMEDILIB_VERSION_MINOR', 'ni_gpct_other_index',
           '_ENDIAN_H', 'W_OK', 'pthread_barrierattr_t', 'O_SYNC',
           'fopencookie', 'pid_t', '__fsfilcnt64_t', 'F_TLOCK',
           'SDF_RUNNING', '__io_read_fn',
           'NI_GPCT_SOURCE_PIN_i_CLOCK_SRC_BITS', 'TIOCPKT',
           'NI_FREQ_OUT_TIMEBASE_2_CLOCK_SRC', 'putc_unlocked',
           'INSN_CONFIG_CHANGE_NOTIFY', '__F_SETOWN_EX', 'ino_t',
           '__sprintf_chk', 'NI_GPCT_STOP_ON_GATE_BITS', '__clock_t',
           '__fsfilcnt_t', 'SIOCGIFMTU', 'INSN_CONFIG_GET_PWM_OUTPUT',
           '__LONG_LONG_PAIR', 'ferror_unlocked', 'F_GETPIPE_SZ',
           'readahead', '_IO_ftrylockfile', 'COMEDI_SUBD_TIMER',
           'TIOCSERSETMULTI', 'feof_unlocked', '_IO_RIGHT',
           '_IOS_APPEND', 'TIOCSER_TEMT', 'fpos64_t',
           '__asprintf_chk', 'NI_GPCT_LOGIC_LOW_CLOCK_SRC_BITS',
           'SDF_MODE4', 'SDF_MODE2', 'SDF_MODE3', 'SDF_MODE0',
           '_G_BUFSIZ', 'COMEDI_RANGEINFO', 'SIOCSIFSLAVE',
           'INSN_CONFIG_ANALOG_TRIG', 'O_APPEND',
           'ni_660x_pfi_routing', 'SIOCGIFBR',
           'NI_GPCT_DISARM_AT_GATE_BITS', '_IO_NO_READS', 'RF_UNIT',
           '__S_IEXEC', '__GLIBC_MINOR__', 'S_IFBLK', 'vscanf',
           'TIOCSERGSTRUCT', 'pthread_barrier_t', '__O_TMPFILE',
           'NI_GPCT_EDGE_GATE_STARTS_STOPS_BITS',
           '__pthread_internal_list', '_IOWR_BAD', 'COMEDI_MAJOR',
           'AMPLC_DIO_GAT_NOUTNM2', 'putchar', 'comedi_cmd',
           'SDF_INTERNAL', '_SYS_SYSMACROS_H',
           'comedi_get_write_subdevice', 'COMEDI_DEVCONF_AUX_DATA_LO',
           'major', 'SIOCGIFBRDADDR', 'pthread_spinlock_t',
           '_IO_seekoff', 'setbuf', 'TIOCPKT_NOSTOP',
           'comedi_conversion_direction', 'NI_GPCT_LOADING_ON_TC_BIT',
           'SDF_CMD_READ', '_IOC_WRITE', 'SIOCGIFINDEX',
           '_IOC_TYPECHECK', '__asprintf', 'CDSUSP', '_IOS_NOCREATE',
           'SWIG_INOUT', 'comedi_mark_buffer_read', 'F_SETSIG',
           'CKILL', '__USE_LARGEFILE', 'I8254_BCD', '_IO',
           'ni_gpct_mode_bits', '_FEATURES_H',
           'NI_CDIO_SCAN_BEGIN_SRC_FREQ_OUT',
           'NI_660X_PFI_OUTPUT_COUNTER', 'vsnprintf',
           '_IO_peekc_locked', 'SIOCGIFMAP', '_IOC_NRSHIFT',
           'LOCK_READ', 'pselect', 'comedi_t_struct', 'O_NONBLOCK',
           '__fread_chk', 'SIOCGIFNETMASK', 'UIO_MAXIOV', 'timeval',
           '_IO_UNBUFFERED', 'O_NDELAY', 'SDF_WRITABLE', 'TCSETXW',
           '__pid_type', 'TIOCSBRK', 'COMEDI_MIN_SPEED', 'TCSETXF',
           'comedi_bufinfo', 'comedi_caldac_t',
           'NI_GPCT_SELECTED_GATE_GATE_SELECT', 'COMEDI_VERSION_CODE',
           'INSN_CONFIG_FILTER', '__pthread_mutex_s',
           '_MKNOD_VER_LINUX', 'NI_PFI_OUTPUT_SCXI_TRIG1', 'mode_t',
           'comedi_cancel', 'TRIG_FOLLOW', 'fputc', 'TIOCOUTQ',
           'NI_PFI_OUTPUT_AI_START_PULSE', 'fputs', 'TIOCM_ST',
           'TIOCM_SR', '__loff_t', 'LOCK_MAND',
           'comedi_get_cmd_src_mask', 'FD_CLR', 'comedi_dio_config',
           'cookie_seek_function_t', 'DN_DELETE', 'FOPEN_MAX',
           'lsampl_t', 'remove', '_IOC_NONE', 'fd_mask',
           'cookie_close_function_t', 'INSN_CONFIG_SERIAL_CLOCK',
           'SIOCSIFBRDADDR', 'INSN_CONFIG_BLOCK_SIZE',
           'COMEDI_SUBD_SERIAL', 'comedi_insn_struct',
           'COMEDILIB_VERSION_MICRO', 'NI_RTSI_OUTPUT_ADR_START2',
           'FNONBLOCK', 'comedi_get_n_subdevices', 'TIOCNXCL',
           'COMEDI_UNSUPPORTED', 'sync_file_range', 'htole16',
           'SDF_RANGETYPE', '__intptr_t', '__timespec_defined',
           'N_SYNC_PPP', 'TIOCEXCL', '__SIZEOF_PTHREAD_BARRIERATTR_T',
           '_IO_flockfile', 'fflush_unlocked', '_IO_DONT_CLOSE',
           'INSN_CONFIG_ALT_SOURCE', 'sys_nerr', '_IO_BAD_SEEN',
           '__BIT_TYPES_DEFINED__',
           'NI_GPCT_ANALOG_TRIGGER_OUT_GATE_SELECT',
           'NI_PFI_OUTPUT_I_ATRIG', 'SIOCGRARP', '__O_DSYNC',
           '__S_IFBLK', 'S_IROTH', 'COMEDI_CMD',
           'NI_PFI_OUTPUT_GOUT1', 'FIOQSIZE', 'file_handle',
           'NI_GPCT_OUTPUT_MODE_MASK', 'u_long', 'comedi_softcal_t',
           'GPCT_DISARM', 'FIOCLEX', 'FASYNC', 'comedi_command_test',
           '_IO_uid_t', 'R_OK', 'NI_CDIO_SCAN_BEGIN_SRC_AI_CONVERT',
           'SIOCSIFPFLAGS', '_IOC_TYPESHIFT', 'ni_rtsi_routing',
           '__USE_XOPEN2K8XSI', '_SYS_CDEFS_H', '_IO_IS_FILEBUF',
           'SEEK_SET', '__io_write_fn', '_IOS_OUTPUT', 'S_IXGRP',
           'TIOCCONS', 'O_EXCL', 'COMEDI_TO_PHYSICAL',
           'comedi_dio_get_config', 'N_PROFIBUS_FDL', 'suseconds_t',
           'NI_GPCT_COUNTING_MODE_NORMAL_BITS', 'F_OWNER_GID',
           'POSIX_FADV_RANDOM', '_IO_LEFT', 'fflush',
           'comedi_get_max_buffer_size',
           'comedi_get_default_calibration_path', 'fd_set',
           'SIOCGIFHWADDR', 'SIOCRTMSG', 'AMPLC_DIO_GAT_GATN',
           'TIOCGEXCL', '_IO_SHOWPOINT', 'NI_PFI_OUTPUT_G_GATE0',
           'NI_PFI_OUTPUT_G_GATE1', 'NI_GPCT_COUNTING_DIRECTION_MASK',
           'TIOCPKT_DATA', '__fread_unlocked_chk', 'O_RDONLY',
           'AREF_DIFF', 'register_t', 'INSN_CONFIG_8254_SET_MODE',
           'comedi_sv_t', '_IOC_NR', 'renameat',
           '__fgets_unlocked_chk', '_IO_vfprintf', '_G_fpos64_t',
           'SIOCGIFCONF', 'tempnam', 'tmpfile', 'TIOCGDEV',
           'COMEDILIB_VERSION_MAJOR',
           'NI_GPCT_COUNTING_DIRECTION_HW_UP_DOWN_BITS',
           '_IO_SHOWPOS', 'COMEDI_EV_SCAN_END', 'COMEDI_LOCK',
           'N_PPP', 'SDF_CMD', 'CINTR', 'fsetpos', '_IOR_BAD',
           'INSN_CONFIG_RESET', '__vfprintf_chk', 'F_GETOWN_EX',
           'comedi_chaninfo_struct', 'COMEDI_INSN',
           'INSN_MASK_SPECIAL', '_IO_peekc', '__USE_BSD', 'TIOCM_RI',
           '__CONCAT', 'SDF_DIFF', 'comedi_get_clock_source',
           '_IOS_NOREPLACE', 'SEEK_CUR', 'S_IFLNK',
           'NI_GPCT_FILTER_TIMEBASE_3_SYNC', 'fopen', 'fgetc',
           'DN_ACCESS', 'daddr_t', '_IO_cookie_file', 'vprintf',
           'TIOCSIG', 'NI_GPCT_COUNTING_DIRECTION_SHIFT', 'u_int',
           'TIOCGWINSZ', '_IO_funlockfile', 'gid_t', 'CR_INVERT',
           'comedi_find_range', 'CERASE', 'F_SHLCK',
           'cookie_read_function_t', 'ungetc', 'comedi_krange',
           'CWERASE', '__codecvt_ok', 'CREPRINT', 'AMPLC_DIO_GAT_GND',
           'COMEDI_COUNTER_TERMINAL_COUNT', 'stat64', 'TRIG_ROUND_UP',
           'N_MASC', 'FIOASYNC', 'LOCK_NB',
           'INSN_CONFIG_PWM_SET_PERIOD', '_IOW_BAD',
           'COMEDI_DEVCONF_AUX_DATA0_LENGTH', '__va_arg_pack_len',
           'comedi_do_insnlist', 'SDF_BUSY_OWNER', 'TIOCINQ',
           'INSN_MASK_WRITE', 'IOCSIZE_MASK', '__codecvt_noconv',
           'TCSETSF', 'NI_GPCT_PRESCALE_X2_CLOCK_SRC_BITS',
           '__glibc_unlikely', 'fclose',
           'NI_GPCT_NEXT_GATE_CLOCK_SRC_BITS', 'TIOCM_RNG',
           'TRIG_ROUND_DOWN', 'fpos_t', '__SIZEOF_PTHREAD_CONDATTR_T',
           'getline', 'NI_GPCT_COUNTING_DIRECTION_HW_GATE_BITS',
           'NI_GPCT_COUNTING_MODE_SYNC_SOURCE_BITS', 'TIOCMGET',
           'IOCSIZE_SHIFT', '_IO_putc', '__S_ISGID',
           'comedi_rangeinfo', '__ASMNAME', 'SIOCGIFPFLAGS',
           'snprintf', '__USE_POSIX199309',
           'NI_PFI_OUTPUT_AI_EXT_MUX_CLK', 'NI_PFI_FILTER_6425ns',
           'INSN_CONFIG_GPCT_PULSE_TRAIN_GENERATOR', 'TRIG_BOGUS',
           'id_t', 'O_RDWR', '_G_fpos_t', 'O_TMPFILE',
           '__SIZEOF_PTHREAD_BARRIER_T', 'AMPLC_DIO_CLK_10KHZ',
           '_IOS_BIN', 'S_IFREG',
           'NI_GPCT_EDGE_GATE_NO_STARTS_NO_STOPS_BITS',
           '__printf_chk', 'i8254_mode', '_STAT_VER_KERNEL', '__PMT',
           'NI_PFI_OUTPUT_RTSI0',
           'NI_GPCT_INDEX_PHASE_LOW_A_LOW_B_BITS', 'TIOCGPGRP',
           'fmemopen', 'fsfilcnt64_t', 'NI_PFI_OUTPUT_EXT_STROBE',
           'INSN_CONFIG_DISARM', '_IOC_SIZESHIFT', '__fsblkcnt64_t',
           'S_IFIFO', 'comedi_loglevel', 'INSN_CONFIG_DIO_OUTPUT',
           'BIG_ENDIAN', '__USE_XOPEN_EXTENDED',
           'NI_GPCT_NEXT_SOURCE_GATE_SELECT', 'SEEK_END', 'N_HDLC',
           'timer_t', 'NI_GPCT_INDEX_PHASE_BITSHIFT',
           'NI_MIO_INTERNAL_CLOCK', 'AT_EACCESS', 'CMDF_RAWDATA',
           'f_owner_ex', 'GPCT_SINGLE_PERIOD', 'fprintf',
           'COMEDI_DEVCONF_AUX_DATA1_LENGTH', 'S_IXUSR',
           'sys_errlist', 'NI_GPCT_INVERT_OUTPUT_BIT',
           'POSIX_FADV_DONTNEED', 'SDF_OTHER', 'UNIT_none',
           'vasprintf', '_IO_free_backup_area', 'TIOCSTI', 'key_t',
           '__USE_ISOC95', 'N_R3964', 'GPCT_CONT_PULSE_OUT',
           '__USE_ISOC99', '_IO_fpos_t', 'comedi_dio_bitfield2',
           'NI_GPCT_SOURCE_PIN_i_GATE_SELECT', 'F_SETOWN_EX',
           'ssize_t', 'le32toh', 'NI_PFI_OUTPUT_AI_START1',
           'NI_PFI_OUTPUT_AI_START2', 'TIOCGETD', '__USE_XOPEN',
           'F_SETPIPE_SZ', '__syscall_slong_t',
           'NI_GPCT_RELOAD_SOURCE_SWITCHING_BITS', 'LITTLE_ENDIAN',
           '__USE_ATFILE', 'NI_FREQ_OUT_TIMEBASE_1_DIV_2_CLOCK_SRC',
           'TMP_MAX', 'NI_MIO_RTSI_CLOCK', '_FCNTL_H', 'TIOCSPGRP',
           'SIOCGARP', 'NI_GPCT_INVERT_CLOCK_SRC_BIT', '__int32_t',
           'ni_pfi_filter_select', '__POSIX_FADV_DONTNEED',
           '_IO_NO_WRITES', '_IOC_DIRMASK', '__F_GETSIG',
           '__FILE_defined', 'comedi_get_driver_name',
           'SYNC_FILE_RANGE_WAIT_AFTER', 'clock_t', 'TIOCSRS485',
           '_IO_CURRENTLY_PUTTING', '__BYTE_ORDER',
           'comedi_get_n_ranges', 'comedi_calibration_setting_t',
           '__gnuc_va_list', 'CMDF_PRIORITY', 'TCGETX', 'fseeko',
           'COMEDI_DEVINFO', 'TCGETS', 'TCSETA', 'TCSETX', 'TCGETA',
           '_G_IO_IO_FILE_VERSION', 'TCSETS',
           'NI_GPCT_ARM_PAIRED_IMMEDIATE',
           'INSN_CONFIG_GET_CLOCK_SRC', 'comedi_mark_buffer_written',
           '_IO_ssize_t', '__USE_SVID', '_IO_IS_APPENDING', 'scanf',
           '__bswap_constant_32', 'COMEDI_CMDTEST', 'termio',
           'L_ctermid', 'CR_RANGE', 'O_LARGEFILE',
           '__SIZEOF_PTHREAD_RWLOCK_T', '__caddr_t',
           '__obstack_printf_chk',
           'NI_GPCT_COUNTING_MODE_TWO_PULSE_BITS', 'TIOCSLCKTRMIOS',
           'fscanf', 'SDF_PACKED', '__USE_EXTERN_INLINES',
           '__SIZEOF_PTHREAD_COND_T', 'SEEK_DATA',
           '__REDIRECT_NTH_LDBL', 'SIOCSIFHWBROADCAST',
           'NI_GPCT_GATE_ON_BOTH_EDGES_BIT',
           'comedi_get_buffer_contents', 'ni_gpct_clock_source_bits',
           'CR_ALT_FILTER', 'TRIG_OTHER', 'SIOCDIFADDR',
           '_XOPEN_SOURCE_EXTENDED', 'COMEDI_NDEVCONFOPTS',
           'GPCT_SET_OPERATION', 'INSN_CONFIG_PWM_OUTPUT', 'TIOCMBIS',
           'NI_RTSI_OUTPUT_ADR_START1', 'TIOCGSERIAL', 'TIOCMBIC',
           'CSUSP', 'amplc_dio_clock_source',
           'NI_RTSI_OUTPUT_DA_START1', 'COMEDI_OOR_NAN',
           'SPLICE_F_GIFT', '__quad_t', '_BSD_SOURCE',
           '__obstack_vprintf_chk', '__uid_t', '__O_DIRECTORY',
           'SDF_WRITEABLE', 'COMEDI_EV_START', '_IO_USER_BUF',
           '__USE_LARGEFILE64', 'htobe64', 'F_SETLK64', 'N_AX25',
           'NI_GPCT_STOP_ON_GATE_OR_TC_BITS', 'COMEDI_CB_ERROR',
           'GPCT_RESET', 'TIOCSETD', 'TIOCPKT_IOCTL', 'F_OWNER_PGRP',
           'CS_MAX_AREFS_LENGTH', 'COMEDI_CANCEL',
           'NI_GPCT_NEXT_TC_CLOCK_SRC_BITS', 'NI_PFI_FILTER_2550us',
           '_IO_DELETE_DONT_CLOSE', '__fgets_chk', '__bos',
           'comedi_polynomial_t', '__ssize_t', 'TCXONC', 'int16_t',
           'TCSETAW', 'TRIG_ROUND_MASK', '__sigset_t',
           'COMEDI_UNLOCK', 'SIOCGIFMEM', 'NI_GPCT_ARM_IMMEDIATE',
           'ni_freq_out_clock_source_bits', 'SDF_PWM_HBRIDGE',
           'S_ISGID', 'SDF_DEGLITCH', 'AT_SYMLINK_FOLLOW',
           'AREF_OTHER', '__FD_SETSIZE', 'O_ASYNC', 'O_TRUNC',
           'tmpnam_r', 'ushort', 'clockid_t', '_IO_size_t', 'caddr_t',
           'GPCT_ARM', 'L_tmpnam', 'F_SETFD', '_IOC_DIRSHIFT',
           'tmpfile64', 'F_SETFL', '__USE_MISC', 'IOC_IN', 'obstack',
           'FD_SET', 'SIOCSIFADDR', 'POSIX_FADV_SEQUENTIAL', 'CQUIT',
           '__PTHREAD_MUTEX_HAVE_PREV', '_IOW', '_BITS_BYTESWAP_H',
           'NI_CDIO_SCAN_BEGIN_SRC_ANALOG_TRIGGER',
           'INSN_CONFIG_DIO_OPENDRAIN', '__dev_t', 'vmsplice',
           'L_cuserid', 'O_FSYNC', '__dprintf_chk', 'vsprintf',
           'rename', '__USE_POSIX199506', '__BIG_ENDIAN',
           'NI_PFI_OUTPUT_PFI_DO', 'comedi_set_filter',
           'fwrite_unlocked', 'COMEDI_DEVCONF_AUX_DATA3_LENGTH',
           'getc', 'INSN_CONFIG_GET_HARDWARE_BUFFER_SIZE',
           'comedi_dio_write', 'comedi_get_maxdata', 'gets', 'getw',
           'TIOCGSOFTCAR', 'SIOGIFINDEX', '__ino_t', '_SYS_IOCTL_H',
           '__REDIRECT_LDBL', 'COMEDI_CB_BLOCK',
           'INSN_CONFIG_GET_PWM_STATUS', '__POSIX_FADV_NOREUSE',
           'be16toh', 'creat64',
           'COMEDI_MAX_NUM_POLYNOMIAL_COEFFICIENTS', '_IOC_READ',
           'S_IRUSR', '__ino64_t', 'INSN_CONFIG_BIDIRECTIONAL_DATA',
           'SIOCGIFENCAP', 'TIOCVHANGUP', 'S_IRGRP', '_SYS_SELECT_H',
           'TIOCLINUX', 'comedi_insnlist', '_ISOC95_SOURCE',
           'NI_GPCT_COUNTING_MODE_MASK', '_IOC_SIZEBITS',
           '__io_close_fn', '_BITS_STAT_H', 'pclose', 'AT_EMPTY_PATH',
           '__fdelt_warn', 'COMEDI_BUFCONFIG', '__clock_t_defined',
           '_STDIO_H', 'IOC_OUT',
           'NI_GPCT_COUNTING_MODE_QUADRATURE_X1_BITS',
           'CR_PACK_FLAGS', 'RANGE_LENGTH', '__SYSCALL_WORDSIZE',
           'fgetc_unlocked', '_IO_UPPERCASE', 'GPCT_GET_INT_CLK_FRQ',
           '_IO_EOF_SEEN', 'TCSETSW', 'AMPLC_DIO_CLK_EXT',
           'NI_GPCT_DISARM_AT_TC_OR_GATE_BITS', 'O_NOATIME',
           'NI_GPCT_TIMEBASE_2_CLOCK_SRC_BITS', 'SDF_LSAMPL',
           'F_GETFD', 'F_GETFL', 'SPLICE_F_MOVE', 'TIOCPKT_START',
           '_ISOC11_SOURCE', 'comedi_close', '__USE_UNIX98',
           'fgets_unlocked', '__gid_t', 'O_CLOEXEC',
           'comedi_counter_status_flags', '_IO_OCT', '__daddr_t',
           'SIOCGIFDSTADDR', 'comedi_rangeinfo_struct', 'SIOCSARP',
           'NI_PFI_OUTPUT_DIO_CHANGE_DETECT_RTSI', '_IO_getc',
           'SIOCADDDLCI', 'cuserid', 'COMEDI_UNKNOWN_SUPPORT',
           'TCSETAF', 'sscanf', 'SIOCSIFNETMASK', 'CIO',
           '_IO_FLAGS2_USER_WBUF', 'TRIG_ROUND_UP_NEXT', 'int64_t',
           'NI_GPCT_LOAD_B_SELECT_BIT', 'le64toh',
           'NI_PFI_OUTPUT_PFI_DEFAULT', '_IO_MAGIC_MASK', 'S_IFCHR',
           'NI_PFI_OUTPUT_GOUT0', 'stat', 'N_X25', 'FD_SETSIZE',
           'NI_CDIO_SCAN_BEGIN_SRC_PXI_STAR_TRIGGER',
           '__codecvt_error', 'O_DIRECT', 'comedi_get_buffer_offset',
           'NI_GPCT_COUNTING_DIRECTION_UP_BITS', 'comedi_open',
           'INSN_CONFIG_PWM_GET_H_BRIDGE',
           'NI_PFI_OUTPUT_PXI_STAR_TRIGGER_IN', 'TIOCM_CTS',
           'COMEDI_SUBD_UNUSED', 'TRIG_WAKE_EOS', '_IOC_DIRBITS',
           '_IOLBF', 'NI_GPCT_PXI_STAR_TRIGGER_CLOCK_SRC_BITS',
           'AT_FDCWD']
