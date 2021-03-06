#!/bin/bash
#  Create JPG images of first page of a set of PDFs.
#  usage: pdf_src_dir image_dest_dir

function usage(){
  echo "Usage:  pdf_src_dir image_dest_dir"
  exit 1
}

if [ $# -ne 2 ]; then
    usage
fi
SRC_DIR="$1"
DEST_DIR="$2"

cd $SRC_DIR

for j in *.pdf ; do  
    JPG_NAME=$(basename $j .pdf).jpg 
    convert "$j"'[0]' -background white -alpha remove  -equalize -quality 95 -thumbnail 156x -gravity north -extent 224x224   $DEST_DIR/$JPG_NAME  2>&1 | sed "s/^/$j: /" 
    [ ! -e $DEST_DIR/$JPG_NAME ]  &&  continue
    FSIZE=$(stat --printf="%s" $DEST_DIR/$JPG_NAME)
    if [ $FSIZE -lt 3000 ]; then
        # reject, probably blank
        rm $DEST_DIR/$JPG_NAME
    fi
done
