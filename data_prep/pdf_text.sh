#!/bin/bash
MY_DIR=$(cd $(dirname $0); pwd)

PDF=$1
TARGET_DIR=$2
[ -z "$TARGET_DIR" ] && TARGET_DIR=$(dirname $PDF)

for j in $PDF ; do
  TFILE=$TARGET_DIR/$(basename $j .pdf).txt
  if [ ! -e $TFILE ] ; then 
    # need to extract text
    pdftotext -nopgbrk  -eol unix $j $TFILE
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
