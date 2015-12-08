# vim: ts=2:sw=2:tw=80:nowrap

### we are importing comedi (the python package provided by comedi)
### because of a few inline functions that do not exist in the c library (and
### are not macros).
### This is the set of inline functions that we take from the swig interface:
###   NI_AO_SCAN_BEGIN_SRC_PFI
###   NI_AO_SCAN_BEGIN_SRC_RTSI
###   NI_CDIO_SCAN_BEGIN_SRC_PFI
###   NI_CDIO_SCAN_BEGIN_SRC_RTSI
###   NI_EXT_PFI
###   NI_EXT_RTSI
###   NI_GPCT_GATE_PIN_GATE_SELECT
###   NI_GPCT_PFI_CLOCK_SRC_BITS
###   NI_GPCT_PFI_GATE_SELECT
###   NI_GPCT_PFI_OTHER_SELECT
###   NI_GPCT_RTSI_CLOCK_SRC_BITS
###   NI_GPCT_RTSI_GATE_SELECT
###   NI_GPCT_SOURCE_PIN_CLOCK_SRC_BITS
###   NI_GPCT_UP_DOWN_PIN_GATE_SELECT
###   NI_MIO_PLL_RTSI_CLOCK
###   NI_PFI_OUTPUT_RTSI
###   NI_RTSI_OUTPUT_RTSI_BRD
###   NI_USUAL_PFI_SELECT
###   NI_USUAL_RTSI_SELECT
###
### Couple of options to solve this dilemma:
### 1) have these compiled and stored as extern lib functions
### 2) redef these as macros so that the make_ctypeslib.sh script picks them up
###    automatically
### 3) reimplement in python directly

from comedi import *
from ctypeslib_comedi import *
