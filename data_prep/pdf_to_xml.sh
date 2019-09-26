#!/bin/bash
MY_DIR=$(cd $(dirname $0); pwd)

$MY_DIR/pdfalto -noImage -noImageInline -readingOrder $1  $(dirname $1)/$(basename $1 .pdf).xml
rm -f $(dirname $1)/$(basename $1 .pdf).metadata.xml
