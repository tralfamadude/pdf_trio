# research-pub

Machine Learning (ML) classifier of PDFs whether a doc is a "research publication" using an ensemble of classifiers. It includes a URL based classifier for quick assessment. 

## Env Vars

The following env vars must be defined to run this API service:

- `FT_MODEL` full path to the FastText model for linear classifier
- `FT_URL_MODEL` path to FastText model for URL classifier
- `TEMP` path to temp area, /tmp by default
- `TF_IMAGE_SERVER_HOSTPORT` the host:port for tensorflow-serving process

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

- install on ubuntu (docker.io distinguishes Docker from some preexisting docker thing):
-- `sudo apt-get install docker.io`
- get a docker image from the docker hub  (might need to be careful about v1.x to v2.x transition)
-- `sudo docker pull tensorflow/serving:latest`
-- NOTE: I am running docker at system level (not user), so sudo is needed for operations
- see what is running:
-- `sudo docker ps`
- stop a running docker:
-- `sudo docker stop 955d531040b2`
- to start tensorflow-serving:
-- `./start_serving.sh`
