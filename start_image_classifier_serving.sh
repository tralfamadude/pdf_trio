#!/bin/bash
HERE=$(cd $(dirname $0); pwd)

# if not in env, supply a default path to the fine-tuned image saved model
#  The full absolute path to the basename_for_dataset directory from  is needed here.
[ -z "$IMAGE_MODEL_PATH" ]  &&   IMAGE_MODEL_PATH=${HERE}/../image_model

#  env vars:  -e NAME=value
TUNING="-e TF_XLA_FLAGS=--tf_xla_cpu_global_jit -e KMP_AFFINITY=granularity=fine,compact,1,0 -e KMP_BLOCKTIME=0 -e OMP_NUM_THREADS=8"
sudo docker run -p 8501:8501 --name tf_hub_image  --mount type=bind,source=${IMAGE_MODEL_PATH},target=/models/tensorflow_model $TUNING -e MODEL_NAME=tensorflow_model  -t tensorflow/serving

