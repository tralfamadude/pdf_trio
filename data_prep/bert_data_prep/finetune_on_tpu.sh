#!/bin/bash
BUCKET=$1

# NOTE: this is not completely ready to run since values will be different for a different account, or when
#  a different pre-trained model is used, or timestamp-based files are used in the cloud storage.
# Best approach is to use this as a guide.

# Tested on ubuntu16 on gcp using v2-8 TPU (named tpu-node-1)

#  On the ubuntu16 in google cloud...
# install miniconda
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh >Miniconda3-latest-Linux-x86_64.sh
chmod +x *.sh
./Miniconda3-latest-Linux-x86_64.sh

source ~/.bashrc
# should be in (base) conda env

# create tensorflow_hub env
conda create --name tf_hub python=3.7 scipy  tensorflow=1.14.0 tensorboard=1.14.0 numpy  tensorflow-hub -c conda-forge

conda activate tf_hub

pip install --upgrade google-api-python-client
pip install --upgrade oauth2client


#  When using cloud TPU, cloud storage (gs://) must be used for pretrained model 
#      and the output directory, as indicated by bert repo readme.
#      Also I put the inputs into gs://${BUCKET}/bert_20000
#     
export BERT_BASE_DIR=gs://${BUCKET}/multi_cased_L-12_H-768_A-12

TS=$(date '+%Y%m%dT%H%M')
BOUT=bert_output_$TS

#                          Training
#
nohup python ./run_classifier.py \
--task_name=cola \
--do_train=true \
--do_eval=true \
--vocab_file=$BERT_BASE_DIR/vocab.txt \
--bert_config_file=$BERT_BASE_DIR/bert_config.json \
--init_checkpoint=$BERT_BASE_DIR/bert_model.ckpt \
--max_seq_length=512 \
--train_batch_size=64 \
--learning_rate=2e-5 \
--num_train_epochs=3 \
--do_lower_case=False \
--data_dir=gs://${BUCKET}/$BASE \
--output_dir=gs://${BUCKET}/$BOUT  \
--use_tpu=true \
--tpu_name=tpu-node-1 \
--tpu_zone=us-central1-b \
--num_tpu_cores=8 \
  >run.out 2>&1  & 

# wait for it to finish before proceeding
wait
# OLD: model checkpoint name and bert_output dir MUST be manually substituted below to use largest value ckpt

# savedmodel format.
# next level dir is Unix epoch number that is not the logical version (but could be, in a pinch)
SAVED_MODEL=gs://${BUCKET}/bert_finetuned_${TS}

#          Testing
#
python ./run_classifier.py \
--task_name=cola \
--do_predict=true \
--vocab_file=$BERT_BASE_DIR/vocab.txt \
--bert_config_file=$BERT_BASE_DIR/bert_config.json \
--init_checkpoint=gs://${BUCKET}/${BOUT}/model.ckpt-1136 \
--max_seq_length=512 \
--data_dir=gs://${BUCKET}/bert_20000 \
--use_tpu=true \
--tpu_name=tpu-node-1 \
--tpu_zone=us-central1-b \
--num_tpu_cores=8 \
--output_dir=gs://${BUCKET}/${BOUT}   2>&1 | tee measure.out

#  Back in research-pub/bert_finetune/ (not in google cloud)
# measure withheld samples:
gsutil cp gs://${BUCKET}/${BOUT}/test_results.tsv .
gsutil cp gs://${BUCKET}/bert_20000/test_original.tsv .
python ./evaluate_test_set_predictions.py --tsv ./test_original.tsv --results ./test_results.tsv > test_tally

# see test_tally for details on results on witheld samples

