#!/bin/bash
MY_DIR=$(cd $(dirname $0); pwd)

TARGET_DIR=$2
[ -z "$TARGET_DIR" ] && TARGET_DIR=$(dirname $1)

$MY_DIR/pdfalto -noText -noImage -noImageInline -readingOrder $1  $TARGET_DIR/$(basename $1 .pdf).xmlnt 2>&1 | sed "s|^|$1: |" 
rm -f $TARGET_DIR/$(basename $1 .pdf).xmlnt_metadata.xml
