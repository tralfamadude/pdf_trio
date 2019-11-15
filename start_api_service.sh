#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate research-pub

export FT_MODEL=../fastText/dataset20000.bin
export FT_URL_MODEL=../fastText/url_test_20000.bin
export TF_IMAGE_SERVER_HOSTPORT=localhost:8501
export TF_BERT_VOCAB_PATH=../bert_model_base_multilingual/multi_cased_L-12_H-768_A-12/vocab.txt
export TF_BERT_SERVER_HOSTPORT=localhost:8601


if [ ! -e ./app.py ]; then
  echo "the current working dir. ($(pwd)) does not have the required app.py"
  exit 1
fi

flask run -h localhost -p 3939
