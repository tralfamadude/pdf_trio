#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate pdf_trio

export FLASK_RUN_PORT=3939
export FLASK_APP=pdf_trio
export FT_MODEL=../pdf_trio_models/fastText_models/dataset20000_20190818.bin
export FT_URL_MODEL=../pdf_trio_models/fastText_models/url_dataset20000_20190817.bin
export TF_IMAGE_SERVER_URL="http://localhost:8501/v1"
export TF_BERT_VOCAB_PATH=../pdf_trio_models/bert_models/multi_cased_L-12_H-768_A-12_vocab.txt
export TF_BERT_SERVER_HOSTPORT="http://localhost:8601/v1"

flask run -h localhost
