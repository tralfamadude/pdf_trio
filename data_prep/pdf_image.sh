#!/bin/bash
DEST=.
[ ! -z "$1" ]  &&  DEST="$1"
for j in *.pdf ; do  
    convert "$j"'[0]' -background white -alpha remove  -equalize -quality 95 -thumbnail 156x -gravity north -extent 224x224   $DEST/$(basename $j .pdf).jpg  2>&1 | sed "s/^/$j: /" 
    [ ! -e $(basename $j .pdf).jpg ]  &&  continue
    FSIZE=$(stat --printf="%s" $(basename $j .pdf).jpg)
    if [ $FSIZE -lt 3000 ]; then
        # reject, probably blank
        rm $(basename $j .pdf).jpg
    fi
done
