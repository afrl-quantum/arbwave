#!/bin/sh
TMP=$(mktemp)
h2xml -c /usr/include/comedi.h  /usr/include/comedilib.h -o ${TMP}
xml2py ${TMP} -lcomedi -o ctypeslib_comedi.py
rm ${TMP}
