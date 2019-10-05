#!/bin/bash
# prepare training data for BERT
function usage(){
  echo "Usage:  basename_for_dataset dest_dir kill_list other_pdfs_dir research_pdfs_dir_1 [research_pdfs_dir_2]"
  exit 1
}

HERE=$(cd $(dirname $0); pwd)

if [ $# -lt 5  -o  $# -gt 6 ]; then
    usage
fi
BASE="$1"
DEST_DIR="$2"
KILL_LIST="$3"
OTHER_PDFS_DIR="$4"
RESEARCH_PDFS_DIR_1="$5"
RESEARCH_PDFS_DIR_2="$6"

eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate tf_hub

#  extract text from pdf dir to a txt dir
function extract_text_from_pdfs() {
  local SRC_DIR=$1
  local DEST_DIR=$2
  $HERE/../pdf_text.sh $SRC_DIR $DEST_DIR
}

#     check args
[ -z "$DEST_DIR" ]  &&  usage
if [ -e $DEST_DIR/$BASE ]; then
  echo "already exists: ${DEST_DIR}/${BASE}"
  echo "pick a new base or remove the old directory"
  exit 2
fi
mkdir $DEST_DIR/$BASE
DEST_DIR=$DEST_DIR/$BASE
mkdir -p $DEST_DIR/staging/research
mkdir -p $DEST_DIR/staging/other
[ ! -d "$DEST_DIR" ]  &&  echo "could not create directory: $DEST_DIR"  &&  usage
[ -z "$OTHER_PDFS_DIR"  -o   ! -d "$OTHER_PDFS_DIR" ]  &&  echo "directory does not exist: $OTHER_PDFS_DIR"  &&  usage
[ -z "$RESEARCH_PDFS_DIR_1"  -o   ! -d "$RESEARCH_PDFS_DIR_1" ]  &&  echo "directory does not exist: $RESEARCH_PDFS_DIR_1"  &&  usage
if [ ! -z "$RESEARCH_PDFS_DIR_2" ]; then
  if [ ! -d "$RESEARCH_PDFS_DIR_2" ]; then
     echo "directory does not exist: $RESEARCH_PDFS_DIR_2"
     usage
  else
    # abs path
    RESEARCH_PDFS_DIR_2=$(cd $RESEARCH_PDFS_DIR_2; pwd)
  fi
fi

# convert PDFs to text and put under staging dir corresponding to class
extract_text_from_pdfs $OTHER_PDFS_DIR $DEST_DIR/staging/other
extract_text_from_pdfs $RESEARCH_PDFS_DIR_1 $DEST_DIR/staging/research
[ ! -z "$RESEARCH_PDFS_DIR_2" ]  &&  extract_text_from_pdfs $RESEARCH_PDFS_DIR_2 $DEST_DIR/staging/research

./gen_bert_data.py --category 0 --input $DEST_DIR/staging/other --output $DEST_DIR/0.tsv --max_tokens 512
./gen_bert_data.py --category 1 --input $DEST_DIR/staging/research --output $DEST_DIR/1.tsv --max_tokens 512

# now we have two tsv files that need to be combined, and shuffled to remove ordering bias,
#   after 'other' is cleaned via kill list

function apply_kill_list() {
  local tsv_file=$1
  K=0
  cp $tsv_file /tmp/$$.tsv
  for j in $(cat $KILL_LIST); do
    if (grep -v $j /tmp/$$.tsv > /tmp/$$.2.tsv); then
      let K=K+1
      mv /tmp/$$.2.tsv /tmp/$$.tsv
    fi
  done
  cp /tmp/$$.tsv $tsv_file
  rm /tmp/$$.tsv
  echo "$K items removed by kill list"
}

#  extra cleaning for 'other'
apply_kill_list $DEST_DIR/0.tsv

cat $DEST_DIR/0.tsv $DEST_DIR/1.tsv | shuf - > $DEST_DIR/all_shuffled.tsv
N=$(wc -l $DEST_DIR/all_shuffled.tsv | awk '{ print $1 }')
let "N_TENTH=N/10"
let "N_FIFTH=2*N_TENTH"
let "NTRAIN=N-N_FIFTH"
head -$NTRAIN $DEST_DIR/all_shuffled.tsv > $DEST_DIR/train.tsv

tail -$N_FIFTH $DEST_DIR/all_shuffled.tsv | head -$N_TENTH > $DEST_DIR/dev.tsv
tail -$N_TENTH $DEST_DIR/all_shuffled.tsv > $DEST_DIR/test_original.tsv
echo -e "id\ttext" > $DEST_DIR/test.tsv
cat $DEST_DIR/test_original.tsv | awk -F $'\t'  '{ printf("%s\t%s\n", $1,$4) }' >> $DEST_DIR/test.tsv

echo "all data:      $DEST_DIR/all_shuffled.tsv  (not needed for training or testing)"
echo "training data: $DEST_DIR/train.tsv"
echo "dev data data: $DEST_DIR/dev.tsv (used during training)"
echo "test data:     $DEST_DIR/test.tsv  (withheld for post-training test)"
