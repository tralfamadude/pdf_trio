#!/bin/bash
# process one .pdf file
FPDF=$1
CLASS=$2
TARGET_DIR=$3

# This creates a *.ft and *.txt files in the TARGET_DIR for fastText training for one input PDF.
# Existing *.ft file will be replaced. The *.ft file will not have an EOL char so more tokens can be appeneded.
# If TARGET_DIR is not specified, then files will be created in the same dir as the PDF file.

MY_DIR=$(cd $(dirname $0); pwd)

function usage() {
    echo "usage: file.pdf class [opt_target_dir]"
    echo "example: foo.pdf research"
    echo "example: foo.pdf other /someplace/"
    echo "files are created in the opt_target_dir which defaults to pdf dir"
    exit 1
}

[ -z "$FPDF" ]  &&  usage
[ -z "$CLASS" ]  &&  usage

[ ! -e "$FPDF" ]  &&  echo "${0}: does not exist: $FPDF"

FID=$(basename $FPDF .pdf)
BDIR=$(cd $(dirname $FPDF); pwd)
FPDF=$(basename $FPDF)
[ -z "$TARGET_DIR" ] && TARGET_DIR=$BDIR

#echo "BDIR=$BDIR  FID=$FID  FPDF=$FPDF"

# generate txt if missing
if [ ! -e $TARGET_DIR/$FID.txt ]; then
    # obtain txt
    $MY_DIR/../pdf_text.sh $BDIR/$FPDF $TARGET_DIR
fi
# text output can fail (say, image only pdf), so bail if no text
if [ ! -e $TARGET_DIR/$FID.txt ]; then
    echo "${FID}:  no txt made, skipping"
    exit 0
fi

#  use pdfalto to get WIDTH and HEIGHT
#$MY_DIR/pdf_to_xml_notext.sh  $BDIR/$FPDF $TARGET_DIR
#XNT=$TARGET_DIR/$(basename $FPDF .pdf).xmlnt
#if [ -e $XNT ]; then
#  WIDTH_HEIGHT=$($XNT | tr '<'  '\n' | tr '>'  '\n'|grep 'Page1[^0-9]' | tr -d '/' | awk '{ print($4,$5) }' | tr -d '"' | tr -d '=')
#  # example: WIDTH595.26 HEIGHT779.52
#  #  ToDo: compute ratio, and also in api
#fi

# format file with one line for fastText
OFILE=$TARGET_DIR/$FID.ft

echo -n "__label__$CLASS " > $OFILE


if [ -e $TARGET_DIR/$FID.txt ]; then
    # we want all the words on one line, removing punctuation, tolower, remove control chars
    cat $TARGET_DIR/$FID.txt | tr '\n'  ' ' | sed -e "s|\([.\!?,'/()]\)| \1 |g" | tr "[:upper:]" "[:lower:]" |  tr  "[:cntrl:]"  ' ' | tr '[:punct:]'  ' ' | tr -s ' ' >> $OFILE
fi 


$MY_DIR/pdf_to_xml_notext.sh $BDIR/$FPDF $TARGET_DIR
if [ -f $TARGET_DIR/$FID.xmlnt ] ; then
    echo -n " " >> $OFILE
    cat $TARGET_DIR/$FID.xmlnt | tr '<'  '\n' | tr '>'  '\n'|grep 'Page1[^0-9]' |  awk '{ print $4,$5 }' | tr -d '/' | tr -d '=' | tr -d '"' | tr '\n'  ' ' >> $OFILE
fi

# add final EOL
echo "" >>$OFILE
