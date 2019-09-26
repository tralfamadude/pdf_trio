#!/bin/bash
MY_DIR=$(cd $(dirname $0); pwd)

PDF_DIR=$1
KOUNT=0
TS_START=$(date '+%s')
[ -z "$PDF_DIR" ]  &&  PDF_DIR=`pwd`
for j in $PDF_DIR/*.pdf ; do
  TFILE=$(dirname $j)/$(basename $j .pdf).txt
  if [ ! -e $TFILE ] ; then 
    # need to extract text
    pdftotext -nopgbrk  -eol unix $j $TFILE
    let KOUNT=KOUNT+1
  fi
  # check file size
  if [ -e $TFILE ] ; then
    TFILE_SIZE=$(stat -c %s $TFILE)
    # remove zero sized files since we do not want to train on that
    if [ $TFILE_SIZE -lt 500 ] ; then
      #  too small
      rm $TFILE
    fi
  fi
done
TS_FINISH=$(date '+%s')
let T_DELTA=TS_FINISH-TS_START
echo "$KOUNT pdftotext runs in $T_DELTA seconds" 
