# research-pub Classifier

## Purpose
This repo defines a Machine Learning (ML) ensemble of classifiers to predict whether a PDF doc is a 
"research publication". It also includes a URL based classifier for quick assessment. A REST service
takes PDF contents and returns a JSON for the classification result. 

The purpose of this project is to identify research works for richer cataloging in production 
at [Internet Archive](https://archive.org). Research 
works are not always found in well-curated locations with good metadata that can be utilized 
to enrich indexing and search. Ongoing work at the Internet Archive will use this classifier ensemble
to curate "long tail" research articles in multiple languages. 

The performance target is to classify a PDF in about 1 second on average and this 
implementation achieves that goal when multiple, parallel requests are made on a 
multi-core machine. 

The URL classifier is best used as a "true vs. unknown" choice, that is, if the classification is 
non-research ('other'), then find out more. Our motivation is to have a quick check that can be used
during crawling. The training should be biased toward 

## Implementation Overview

* REST API based on python Flask
* Deep Learning neural networks 
  * Run with tensorflow serving for high throughput
  * CNN for image classification
  * BERT for text classification using a multilingual model
* FastText linear classifier
  * Full text 'bag of words' classification
  * URL-based classification
* PDF training data preparation scripts (./data_prep)

Two other repos are relied upon and not copied into this repo because they are useful standalone. This repo 
can be considered the 'roll up' that integrates the ensemble.  

### PDF Challenges

PDFs have challenges, because they can: 
* be pure images of text with no easily extractable text at all 
* range from 1 page position papers to 100+ page theses
* have citations either at the end of the document, or interspersed as footnotes 

We decided to avoid using OCR for text extraction for speed reasons and because of the challenge of multiple languages.  

We address these challenges with an ensemble of classifiers that use confidence values
to cover all the cases. There are still some edge cases, but incidence rate is at most a few percent.

---

## Setup 

## Env Vars

The following env vars must be defined to run this API service:

- `FT_MODEL` full path to the FastText model for linear classifier
- `FT_URL_MODEL` path to FastText model for URL classifier
- `TEMP` path to temp area, /tmp by default
- `TF_IMAGE_SERVER_HOSTPORT` host:port for image tensorflow-serving process
- `TF_BERT_SERVER_HOSTPORT` host:port for BERT tensorflow-serving process

## REST API service Setup


These directions assume you are running in an Ubuntu Xenial (16.04 LTS) virtual machine.

```
sudo apt-get install -y poppler-utils imagemagick libmagickcore-6.q16-2-extra ghostscript netpbm gsfonts-other
conda create --name research-pub python=3.7 --file requirements.txt
conda activate research-pub
```
edit /etc/ImageMagick/policy.xml to change: 
```
<policy domain="coder" rights="none" pattern="PDF" />
```
To: 
```
<policy domain="coder" rights="read" pattern="PDF" />
```

We expect imagemagick 6.x; when 7.x is used, the binary will not be called convert anymore.

## Back-Backend Services

- fastText
- tensorflow-serving for image inference
- BERT (via tf-serving or bert-server)

### Models

You need to find/download the following model files or directories:

    ../bert_finetuned_20190923T2215     (1.3G)
    ../fastText/dataset20000.bin        (637M)
    ../fastText/url_test_20000.bin      (194M)
    ../bert_model_base_multilingual     (680M)



### Tensorflow-Serving via Docker

Tensorflow serving is used to host the NN models and we prefer to use the REST because that significantly 
reduces the complexity on the client side.  

- install on ubuntu (docker.io distinguishes Docker from some preexisting package 'docker', a window manager extension):
  - `sudo apt-get install docker.io`
- get a docker image from the docker hub  (might need to be careful about v1.x to v2.x transition)
  - `sudo docker pull tensorflow/serving:latest`
  - NOTE: I am running docker at system level (not user), so sudo is needed for operations, YMMV
- see what is running:
  - `sudo docker ps`
- stop a running docker, using the id shown in the docker ps output:
  - `sudo docker stop 955d531040b2`
- to start tensorflow-serving:
  - `./start_bert_serving.sh`
  - `./start_image_classifier_serving.sh`
