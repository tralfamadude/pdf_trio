#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate research-pub

export FT_MODEL=/home/peb/ws/fastText/dataset20000.bin
export FT_URL_MODEL=/home/peb/ws/fastText/url_test_20000.bin
export TF_IMAGE_SERVER_HOSTPORT=localhost:6800

if [ ! -e ./app.py ]; then
  echo "the current working dir. ($(pwd)) does not have the required app.py"
  exit 1
fi

flask run -h localhost -p 3939
