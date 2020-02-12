#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate pdf_trio

export FT_MODEL=../pdf_trio_models/fastText_models/dataset20000_20190818.bin
export FT_URL_MODEL=../pdf_trio_models/fastText_models/url_dataset20000_20190817.bin
export TF_IMAGE_SERVER_HOSTPORT=localhost:8501
export TF_BERT_VOCAB_PATH=../pdf_trio_models/bert_models/multi_cased_L-12_H-768_A-12_vocab.txt
export TF_BERT_SERVER_HOSTPORT=localhost:8601


if [ ! -e ./app.py ]; then
  echo "the current working dir. ($(pwd)) does not have the required app.py"
  exit 1
fi

flask run -h localhost -p 3939
