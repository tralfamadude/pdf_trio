#!/bin/bash
MY_DIR=$(cd $(dirname $0); pwd)
#  usage: pdf_file dest_dir

function usage() {
    echo "usage: file.pdf [opt_target_dir]"
    exit 1
}

PDF=$1
[ ! -z "$PDF" ]  &&  usage
TARGET_DIR=$2
[ ! -z "$TARGET_DIR" ]  &&  usage

TFILE=$TARGET_DIR/$(basename $PDF .pdf).txt
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
