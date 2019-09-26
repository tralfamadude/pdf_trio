#!/bin/bash

#  env vars:  -e NAME=value

TUNING="-e TF_XLA_FLAGS=--tf_xla_cpu_global_jit -e KMP_AFFINITY=granularity=fine,compact,1,0 -e KMP_BLOCKTIME=0 -e OMP_NUM_THREADS=8"
sudo docker run -p 8501:8501 --name tf_hub_image  --mount type=bind,source=/home/peb/ws/tf_hub_image_classifier_serving/models,target=/models/tensorflow_model $TUNING -e MODEL_NAME=tensorflow_model  -t tensorflow/serving

