# research-pub

Machine Learning (ML) classifier of PDFs whether a doc is a "research publication" using an ensemble of classifiers. It includes a URL based classifier for quick assessment. 
## Env Vars
The following env vars must be defined to run this API service
* FT_MODEL full path to the FastText model for linear classifier
* FT_URL_MODEL path to FastText model for URL classifier
* TEMP path to temp area, /tmp by default
* TF_IMAGE_SERVER_HOSTPORT the host:port for tensorflow-serving process

## REST API service Setup
conda create --name research-pub python=3.7  numpy flask
conda activate research-pub
pip install fasttext
pip install -r requirements.txt
sudo apt-get install poppler-utils
sudo apt-get install imagemagick

## Back-Backend Services
* fastText
* tensorflow-serving
* BERT
