#!/bin/bash
BASE="$1"
[ -z "$BASE" ]  &&  echo "usage: basename_for_dataset"  &&  exit 1

#  train fastText
./fasttext supervised -input   ${BASE}.samples.train -output ${BASE} -lr 1.0 -dim 50 -epoch 2
#  check against validation set
./fasttext test ${BASE}.bin ${BASE}.samples.validate

