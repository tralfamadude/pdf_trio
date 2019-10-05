#!/bin/bash
# full text dataset prep for FastText

function usage(){
  echo "Usage:  basename_for_dataset dest_dir other_pdfs_dir research_pdfs_dir_1 [research_pdfs_dir_2]"
  exit 1
}

HERE=$(cd $(dirname $0); pwd)

if [ $# -lt 4  -o  $# -gt 5 ]; then
    usage
fi
BASE="$1"
DEST_DIR="$2"
OTHER_PDFS_DIR="$3"
RESEARCH_PDFS_DIR_1="$4"
RESEARCH_PDFS_DIR_2="$5"

#     check args
[ -z "$DEST_DIR" ]  &&  usage
mkdir -p $DEST_DIR/$BASE
DEST_DIR=$DEST_DIR/$BASE
if [ -d $DEST_DIR/staging ]; then
  # remove old ft files so do not have unwitting accumulation
  rm -rf $DEST_DIR/staging
fi
mkdir -p $DEST_DIR/staging
[ ! -d "$DEST_DIR" ]  &&  echo "could not create directory: $DEST_DIR"  &&  usage
[ -z "$OTHER_PDFS_DIR"  -o   ! -d "$OTHER_PDFS_DIR" ]  &&  echo "directory does not exist: $OTHER_PDFS_DIR"  &&  usage
[ -z "$RESEARCH_PDFS_DIR_1"  -o   ! -d "$RESEARCH_PDFS_DIR_1" ]  &&  echo "directory does not exist: $RESEARCH_PDFS_DIR_1"  &&  usage
if [ ! -z "$RESEARCH_PDFS_DIR_2" ]; then
  if [ ! -d "$RESEARCH_PDFS_DIR_2" ]; then
     echo "directory does not exist: $RESEARCH_PDFS_DIR_2"
     usage
  else
    # abs path
    RESEARCH_PDFS_DIR_2=$(cd $RESEARCH_PDFS_DIR_2; pwd)
  fi
fi

echo "The .ft files will be staged in ${DEST_DIR}/staging and fastText training files will be put in ${DEST_DIR}"

# make paths absolute since we will use cd
DEST_DIR=$(cd $DEST_DIR; pwd)
OTHER_PDFS_DIR=$(cd $OTHER_PDFS_DIR; pwd)
RESEARCH_PDFS_DIR_1=$(cd $RESEARCH_PDFS_DIR_1; pwd)
# RESEARCH_PDFS_DIR_2 already abs

#  create *.ft files, one for each pdf, with tokens from the pdf
cd $OTHER_PDFS_DIR
for j in *.pdf ; do
  $HERE/prep_fasttext.sh $j other $DEST_DIR/staging
  if [ -e $DEST_DIR/staging/$(basename $j .pdf).txt ]; then
    cat $DEST_DIR/staging/$(basename $j .pdf).txt >>${DEST_DIR}/${BASE}.samples.raw
    # COULD: rm $DEST_DIR/staging/$(basename $j .pdf).txt
  fi
done
cd $RESEARCH_PDFS_DIR_1
for j in *.pdf ; do
  $HERE/prep_fasttext.sh $j research $DEST_DIR/staging
  if [ -e $DEST_DIR/staging/$(basename $j .pdf).txt ]; then
    cat $DEST_DIR/staging/$(basename $j .pdf).txt >>${DEST_DIR}/${BASE}.samples.raw
    # COULD: rm $DEST_DIR/staging/$(basename $j .pdf).txt
  fi
done
if [ ! -z "$RESEARCH_PDFS_DIR_2" ]; then
  cd $RESEARCH_PDFS_DIR_2
  for j in *.pdf ; do
    $HERE/prep_fasttext.sh $j research $DEST_DIR/staging
    if [ -e $DEST_DIR/staging/$(basename $j .pdf).txt ]; then
      cat $DEST_DIR/staging/$(basename $j .pdf).txt >>${DEST_DIR}/${BASE}.samples.raw
      # COULD: rm $DEST_DIR/staging/$(basename $j .pdf).txt
    fi
  done
fi

#            shuffle the sample file
cat ${DEST_DIR}/${BASE}.samples.raw | sort -R >${DEST_DIR}/${BASE}.samples
N=$(wc -l ${DEST_DIR}/${BASE}.samples | awk '{ print $1 }')

#   break up into train/test
let "NTEST=N/9"
let "NTRAIN=N-NTEST"
head -$NTRAIN ${DEST_DIR}/${BASE}.samples > ${DEST_DIR}/${BASE}.samples.train
tail -$NTEST ${DEST_DIR}/${BASE}.samples > ${DEST_DIR}/${BASE}.samples.validate

echo "The .ft files:         ${DEST_DIR}/staging  (can be removed after inspection)"
echo "All data samples: ${DEST_DIR}/${BASE}.samples  N=${N}"
echo "Training data: ${DEST_DIR}/${BASE}.train  N=${NTRAIN}"
echo "Validation data:       ${DEST_DIR}/${BASE}.validate  N=${NTEST}"

