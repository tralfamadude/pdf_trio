#!/bin/bash

#  env vars:  -e NAME=value

TUNING="-e TF_XLA_FLAGS=--tf_xla_cpu_global_jit -e KMP_AFFINITY=granularity=fine,compact,1,0 -e KMP_BLOCKTIME=0 -e OMP_NUM_THREADS=8"
nohup  sudo docker run -p 8601:8501 --name tf_bert  --mount type=bind,source=/home/peb/ws/bert_model_finetuned_20190918T03/,target=/models/bert_model $TUNING -e MODEL_NAME=bert_model  -t tensorflow/serving  >start_bert_serving.out 2>&1 & 

