#!/bin/bash

#  env vars:  -e NAME=value
#  VERBOSE: -e TF_CPP_MIN_VLOG_LEVEL=3  (300MB per day even if doing nothing)
MPATH=$(pwd)/../bert_finetuned_20190923T2215
TUNING="-e TF_XLA_FLAGS=--tf_xla_cpu_global_jit -e KMP_AFFINITY=granularity=fine,compact,1,0 -e KMP_BLOCKTIME=0 -e OMP_NUM_THREADS=8"
nohup  sudo docker run -p 8601:8501 --name tf_bert  --mount type=bind,source=${MPATH}/,target=/models/bert_model $TUNING -e MODEL_NAME=bert_model  -t tensorflow/serving  >/tmp/start_bert_serving.out 2>&1 &

echo "see /tmp/start_bert_serving.out"

