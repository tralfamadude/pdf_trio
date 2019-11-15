#!/bin/bash
MY_DIR=$(cd $(dirname $0); pwd)
#  usage: [src_dir] [dest_dir]
#   by default, uses '.' directory

PDF_DIR=.
[ ! -z "$1" ]  &&  PDF_DIR="$1"
TARGET_DIR=.
[ ! -z "$2" ]  &&  TARGET_DIR="$2"

for j in $PDF_DIR/*.pdf ; do
  $MY_DIR/pdf_one_text.sh $j $TARGET_DIR
done
