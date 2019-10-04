#!/bin/bash
function usage(){
  echo "Usage:  basename_for_dataset dataset_dir path_to_fasttext_dir"
  exit 1
}

if [ $# -ne 3 ]; then
    usage
fi
BASE="$1"
DATA_DIR="$2"
FT_PATH="$3"

#  train fastText
$FT_PATH/fasttext supervised -input ${DATA_DIR}/${BASE}/${BASE}.samples.train -output ${DATA_DIR}/${BASE}/${BASE} -lr 1.0 -dim 50 -epoch 2
#  check against validation set
$FT_PATH/fasttext test ${DATA_DIR}/${BASE}/${BASE}.bin ${DATA_DIR}/${BASE}/${BASE}.samples.validate

