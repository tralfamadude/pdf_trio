#!/bin/bash
# URL dataset prep for FastText

function usage(){
  echo "Usage:  basename_for_dataset dest_dir input_tsv_other input_tsv_research"
  exit 1
}

if [ $# -ne 4 ]; then
    usage
fi
BASE="$1"
DEST_DIR="$2"
INPUT_TSV_OTHER="$3"
INPUT_TSV_RESEARCH="$4"

#     check args
[ -z "$DEST_DIR" ]  &&  usage
DEST_DIR=$DEST_DIR/$BASE
if [ -e $DEST_DIR ]; then
  echo "already exists: ${DEST_DIR}"
  echo "pick a new base or remove the old directory"
  exit 2
fi
mkdir -p $DEST_DIR/staging
[ ! -d "$DEST_DIR" ]  &&  echo "could not create directory: $DEST_DIR"  &&  usage
[ -z "$INPUT_TSV_OTHER"  -o   ! -f "$INPUT_TSV_OTHER" ]  &&  echo "tsv input file does not exist: $INPUT_TSV_OTHER"  &&  usage
[ -z "$INPUT_TSV_RESEARCH"  -o   ! -f "$INPUT_TSV_RESEARCH" ]  &&  echo "tsv input file does not exist: $INPUT_TSV_RESEARCH"  &&  usage

# Example line from tsv file:
# c487656070a636a24800776051e9d5449ebfbdea        https://core.ac.uk/download/pdf/81995083.pdf    201904150928
# notice that all rows in one tsv file correspond to one label (class)

echo "The .ft files will be staged in ${DEST_DIR}/staging and combined fastText training files will be put in ${DEST_DIR}"

# make path absolute
DEST_DIR=$(cd $DEST_DIR; pwd)

#  create *.ft files, one for each row in the tsv files
./preprocess_tsv.py --category research --input $INPUT_TSV_RESEARCH --working  $DEST_DIR/staging
./preprocess_tsv.py --category other --input $INPUT_TSV_OTHER --working  $DEST_DIR/staging

#            gather .ft files together to create sample files and then train/test
( cd ${DEST_DIR}/staging; cat *ft | sort -R >${DEST_DIR}/${BASE}.samples )
N=$(wc -l ${DEST_DIR}/${BASE}.samples | awk '{ print $1 }')
echo "All ${N} data samples: ${DEST_DIR}/${BASE}.samples"

let "NTEST=N/9"
let "NTRAIN=N-NTEST"
head -$NTRAIN ${DEST_DIR}/${BASE}.samples > ${DEST_DIR}/${BASE}.samples.train
tail -$NTEST ${DEST_DIR}/${BASE}.samples > ${DEST_DIR}/${BASE}.samples.validate

echo "Training data: ${DEST_DIR}/${BASE}.train"
echo "Validation data: ${DEST_DIR}/${BASE}.validate"

