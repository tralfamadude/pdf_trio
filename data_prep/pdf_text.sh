#!/bin/bash
MY_DIR=$(cd $(dirname $0); pwd)
#  usage: [src_dir] [dest_dir]
#   by default, uses '.' directory

PDF=.
[ ! -z "$1" ]  &&  PDF="$1"
TARGET_DIR=.
[ ! -z "$2" ]  &&  TARGET_DIR="$2"

for j in $PDF/*.pdf ; do
  TFILE=$TARGET_DIR/$(basename $j .pdf).txt
  if [ ! -e $TFILE ] ; then 
    # need to extract text
    pdftotext -nopgbrk  -eol unix $j $TFILE
  fi
  # check file size
  if [ -e $TFILE ] ; then
    TFILE_SIZE=$(stat -c %s $TFILE)
    # remove small sized files since we do not want to train on that
    if [ $TFILE_SIZE -lt 500 ] ; then
      #  too small
      rm $TFILE
    fi
  fi
done
