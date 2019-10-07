#!/bin/bash
HERE=$(cd $(dirname $0); pwd)
#  env vars:  -e NAME=value
#  VERBOSE: -e TF_CPP_MIN_VLOG_LEVEL=3  (300MB per day even if doing nothing)

# if not in env, supply a default path to the fine-tuned bert model
#  The full absolute path to the basename_for_dataset directory from prep_all_bert.sh is needed here.
[ -z "$BERT_MODEL_PATH" ]  &&   BERT_MODEL_PATH=$(pwd)/../bert_finetuned_20190923T2215
TUNING="-e TF_XLA_FLAGS=--tf_xla_cpu_global_jit -e KMP_AFFINITY=granularity=fine,compact,1,0 -e KMP_BLOCKTIME=0 -e OMP_NUM_THREADS=8"
nohup  sudo docker run -p 8601:8501 --name tf_bert  --mount type=bind,source=${BERT_MODEL_PATH}/,target=/models/bert_model $TUNING -e MODEL_NAME=bert_model  -t tensorflow/serving  >/tmp/start_bert_serving.out 2>&1 &

echo "see /tmp/start_bert_serving.out"

