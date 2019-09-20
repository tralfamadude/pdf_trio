
import fasttext
from fasttext import load_model
import os
import time
import argparse
import text_prep
import pdf_util
import subprocess
import logging
import cv2  # pip install opencv-python  to get this
import numpy as np
import json
import requests
from werkzeug import FileStorage

log = logging.getLogger(__name__)

version_map = {
    "image": "20190708",
    "linear": "20190720",
    "bert": "20190918",
    "urlmeta": "20190722"
}

FT_MODEL = os.environ.get('FT_MODEL')
if not FT_MODEL:
    raise ValueError('Missing fasttext model, define env var FT_MODEL=full_path_to_basename')
fasttext_model = fasttext.load_model(FT_MODEL)

TF_IMAGE_SERVER_HOSTPORT = os.environ.get('TF_IMAGE_SERVER_HOSTPORT')
if not TF_IMAGE_SERVER_HOSTPORT:
    raise ValueError('Missing TF image classifier host:port spec, define env var TF_IMAGE_SERVER_HOSTPORT=host:port')
TF_IMAGE_SERVER_HOST = TF_IMAGE_SERVER_HOSTPORT.split(":")[0]
TF_IMAGE_SERVER_PORT = TF_IMAGE_SERVER_HOSTPORT.split(":")[1]

TF_BERT_SERVER_HOSTPORT = os.environ.get('TF_BERT_SERVER_HOSTPORT')
if not TF_BERT_SERVER_HOSTPORT:
    raise ValueError('Missing TF BERT classifier host:port spec, define env var TF_BERT_SERVER_HOSTPORT=host:port')
TF_BERT_SERVER_HOST = TF_BERT_SERVER_HOSTPORT.split(":")[0]
TF_BERT_SERVER_PORT = TF_BERT_SERVER_HOSTPORT.split(":")[1]

TF_BERT_VOCAB_PATH = os.environ.get('TF_BERT_VOCAB_PATH')
if not TF_BERT_VOCAB_PATH:
    raise ValueError('TF_BERT_VOCAB_PATH is not set to the path to vocab.txt')
if not os.path.exists(TF_BERT_VOCAB_PATH) and os.path.isfile(TF_BERT_VOCAB_PATH):
    raise ValueError('TF_BERT_VOCAB_PATH target does not exist: %s' % TF_BERT_VOCAB_PATH)
bert_vocab = text_prep.load_bert_vocab(TF_BERT_VOCAB_PATH)

json_content_header = {"Content-Type": "application/json"}
image_tf_server_url = "http://%s:%s/v1/models/tensorflow_model:predict" % (TF_IMAGE_SERVER_HOST, TF_IMAGE_SERVER_PORT)

bert_tf_server_url = "http://%s:%s/v1/models/bert_model:predict" % (TF_BERT_SERVER_HOST, TF_BERT_SERVER_PORT)

def classify_pdf_multi(modes, pdf_filestorage):
    """
    Use the modes param to pick subclassifiers and make an ensemble conclusion.

    example result: {"is_research" : 0.94,
                   "image" : 0.96,
                   "linear" : 0.92,
                   "bert" : 0.91,
                   "version" : {
                       "image" : "20190708",
                       "linear" : "20190720",
                       "bert" : "20190807",
                       "urlmeta" : "20190722"
                                }
                   }
    :param modes:  comma sep list of 1 or more {auto, image, linear, bert, all}
    :param pdf_filestorage: as FileStorage object (contains a stream).
    :return: map
    """
    results = {"version": version_map}
    confidence_values = []
    mode_list = modes.split(",")
    pdf_token_list = []
    # rewrite mode_list if 'all' is requested
    if 'all' in mode_list:
        mode_list = ['image', 'linear', 'bert']
    # write pdf content to tmp file
    tmp_pdf_name = pdf_util.tmp_file_name()
    pdf_filestorage.save(tmp_pdf_name)
    log.debug("stored pdf_content for %s in %s" % (pdf_filestorage.filename, tmp_pdf_name))
    # look ahead to see if text is required, so we can extract that now
    if ('linear' in mode_list) or ('bert' in mode_list) or ('auto' in mode_list):
        # extract text
        pdf_raw_text = pdf_util.extract_pdf_text(tmp_pdf_name)
        if len(pdf_raw_text) < 300:
            pdf_token_list = []  # too short to be useful
        else:
            pdf_token_list = text_prep.extract_tokens(pdf_raw_text)
    if 'auto' in mode_list:
        # start with fastest, use confidence thresholds to short circuit
        if len(pdf_token_list) != 0:
            # FastText
            confidence_linear = classify_pdf_linear(pdf_token_list)
            results['linear'] = confidence_linear
            confidence_values.append(confidence_linear)
            if .85 >= confidence_linear >= 0.15:
                # also check BERT
                pdf_token_list_trimmed = text_prep.trim_tokens(pdf_token_list, 512)
                confidence_bert = classify_pdf_bert(pdf_token_list_trimmed)
                results['bert'] = confidence_bert
                confidence_values.append(confidence_bert)
        else:
            # no tokens, so use image
            jpg_file_page0 = pdf_util.extract_pdf_image(tmp_pdf_name)
            # classify pdf_image_page0
            confidence_image = classify_pdf_image(jpg_file_page0)
            results['image'] = confidence_image
            confidence_values.append(confidence_image)
            # remove tmp jpg
            if logging.getLogger().getEffectiveLevel() != logging.DEBUG:
                pdf_util.remove_tmp_file(jpg_file_page0)
    else:
        # apply named classifiers
        for classifier in mode_list:
            if classifier == "image":
                jpg_file_page0 = pdf_util.extract_pdf_image(tmp_pdf_name)
                if len(jpg_file_page0) == 0:
                    log.debug("no jpg for %s" % (pdf_filestorage.filename))
                    continue  # skip
                # classify pdf_image_page0
                confidence_image = classify_pdf_image(jpg_file_page0)
                results[classifier] = confidence_image
                confidence_values.append(confidence_image)
                # remove tmp jpg
                if logging.getLogger().getEffectiveLevel() != logging.DEBUG:
                    pdf_util.remove_tmp_file(jpg_file_page0)
            elif classifier == "linear":
                if len(pdf_token_list) == 0:
                    # cannot use this classifier if no tokens extracted
                    log.debug("no tokens extracted for %s" % (pdf_filestorage.filename))
                    continue  # skip
                confidence_linear = classify_pdf_linear(pdf_token_list)
                results[classifier] = confidence_linear
                confidence_values.append(confidence_linear)
            elif classifier == "bert":
                if len(pdf_token_list) == 0:
                    # cannot use this classifier if no tokens extracted
                    log.debug("no tokens extracted for %s" % (pdf_filestorage.filename))
                    continue  # skip
                pdf_token_list_trimmed = text_prep.trim_tokens(pdf_token_list, 512)
                confidence_bert = classify_pdf_bert(pdf_token_list_trimmed)
                results[classifier] = confidence_bert
                confidence_values.append(confidence_bert)
            else:
                log.warning("ignoring unknown classifier ref: " + classifier)
    if logging.getLogger().getEffectiveLevel() != logging.DEBUG:
        pdf_util.remove_tmp_file(tmp_pdf_name)
    #  compute 'is_research' using confidence_values
    if len(confidence_values) != 0:
        confidence_overall = sum(confidence_values) / len(confidence_values)
        # insert confidence_overall
        results["is_research"] = confidence_overall
    return results


def encode_confidence(label, confidence):
    """
    Encode label,confidence into a single float [0.0, 1.0] so that 1.0 means perfect confidence in positive case,
    and 0.0 is perfect confidence for negative case.
    confidence 0 means 'other', 1.0 means 'research'
    :param label: 'research' or '__label__research' versus 'other' or '__label__other'
    :param confidence: [0.5, 1.0]
    :return: [0.0, 1.0]
    """
    if confidence < 0.5:
        log.error("encode_confidence called improperly with label=%s confidence=%f" % (label, confidence))
    if confidence > 1.0:
        confidence = 1.0
    if confidence < 0.0:
        confidence = 0.0
    if label == '__label__research' or label == 'research':
        return ((confidence / 2) + 0.5)
    else:
        return (0.5 - (confidence / 2))


def decode_confidence(e):
    """
    decode composite confidence
    :param e: combined/encoded confidence
    :return: label, confidence
    """
    if e < 0.5:
        return "other", 1.0 - (2 * e)
    else:
        return "research", (2 * e) - 1.0


def classify_pdf_linear(pdf_token_list):
    """
    Apply fastText model to content

    :param pdf_tokens: cleaned tokens list from pdf content
    :return: encoded confidence as type float with range [0.5,1.0] that example is positive
    """
    #  classify using fastText model
    results = fasttext_model.predict(" ".join(pdf_token_list))
    label = results[0][0]
    confidence = results[1][0]
    log.debug("classify_pdf_linear: label=%s confidence=%.2f" % (label, confidence))
    return encode_confidence(label, confidence)


def classify_pdf_bert(pdf_token_list, trace_id=""):
    """
    Apply BERT model to content to classify given token list.

    :param pdf_tokens: cleaned tokens list from pdf content, trimmed to not exceed max tokens (512)
    :param trace_id: string for doc id, if known.
    :return: encoded confidence as type float with range [0.5,1.0] that example is positive
    """
    token_ids = text_prep.convert_to_bert_vocab(bert_vocab, pdf_token_list)
    tcount = len(token_ids)
    if tcount < 512:
        for j in range(tcount, 512):
            token_ids.append(0)
    # add entries so that token_ids is 512 length
    # for REST request, need examples=[{"input_ids": [], "input_mask":[], "label_ids":[0], "segment_ids":[]}]
    input_ids = token_ids
    if tcount < 512:
        input_mask = np.concatenate((np.ones(tcount, dtype=int),  np.zeros(512-tcount, dtype=int)), axis=0).tolist()
    else:
        input_mask = np.ones(512, dtype=int).tolist()
    label_ids = [0]  # dummy, one int, not needed for prediction
    segment_ids = np.zeros(512, dtype=int).tolist()
    evalue = {"input_ids": input_ids, "input_mask": input_mask, "label_ids": label_ids, "segment_ids": segment_ids}
    req_json = json.dumps({"signature_name": "serving_default", "examples": [evalue]})
    log.debug("BERT: request to %s is: %s ... %s" % (bert_tf_server_url, req_json[:120], req_json[len(req_json)-80:]))
    ret = 0.5  # zero confidence encoded default
    try:
        response = requests.post(bert_tf_server_url, data=req_json, headers=json_content_header)
        if response.status_code == 200:
            response_vec = response.json()["predictions"][0]
            confidence_other = response_vec[0]
            confidence_research = response_vec[1]
            log.debug("bert classify %s  other=%.2f research=%.2f" % (trace_id, confidence_other, confidence_research))
            if confidence_research > confidence_other:
                ret = encode_confidence("research", confidence_research)
            else:
                ret = encode_confidence("other", confidence_other)
        elif response.status_code == 400:
            log.warning("HTTP 400 from tf-serving of bert, %s" % response.json())
    except Exception:
        log.warning("exception occurred processing REST BERT tensorflow-serving for %s" % trace_id)
    return ret



def classify_pdf_image_via_exec(jpg_file):
    """
    Apply image model to content image

    :param jpg_file: tmp jpg image file name, full path.
    :return: encoded confidence as type float with range [0.5,1.0] that example is positive
    """
    ret = 0.5  # lowest confidence encoded value
    myenv = {"dummy": "0",
             "CONDA_DEFAULT_ENV": "tf_hub",
             "CONDA_PYTHON_EXE": "/home/peb/miniconda3/bin/python",
             "HOME": "/home/peb",
             "PATH": "/home/peb/bin:/home/peb/miniconda3/envs/tf_hub/bin:/home/peb/miniconda3/bin:/home/peb/miniconda3/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
             "CONDA_EXE": "/home/peb/miniconda3/bin/conda",
             "CONDA_PREFIX": "/home/peb/miniconda3/envs/tf_hub",
             "CONDA_PREFIX_1": "/home/peb/miniconda3",
             "CONDA_SHLVL":"2"
             }
    w_dir = "../tf_hub_image_classifier"
    cmd = [ w_dir+'/infer_image_new.py', '--image='+jpg_file, '--graph='+w_dir+'/retrained_graph.pb',
            '--labels='+w_dir+'/out/retrained_labels.txt', '--input_layer=Placeholder', '--output_layer=final_result']
    mycwd = "."
    t0 = time.time()
    pp = subprocess.Popen(cmd, encoding='utf-8', env=myenv, cwd=mycwd, bufsize=1, universal_newlines=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs, errs = pp.communicate(timeout=30)
        # dump stderr if DEBUG
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            log.debug("infer_image_new.py stderr: ", errs)
        # parse outs     ex: research 0.5082055 ./tmp/0b4997a068e557eb92b6adf7875248ec7292dd4a.jpg
        lines = outs.split('\n')
        for aline in lines:
            mytokens = aline.split()
            if len(mytokens) < 3:
                continue
            label = mytokens[0]
            if label == "research" or label == "other":
                confidence = float(mytokens[1])
                if confidence > 0.5:
                    ret = encode_confidence(label, confidence)
                    break
    except subprocess.TimeoutExpired:
        pp.kill()
        # drain residue so subprocess can really finish
        outs, errs = pp.communicate()
        log.warning("classify_pdf_image, command did not terminate in %.2f seconds, terminating." % (time.time()-t0))


    #log.info("classify_pdf_image: label=%s confidence=%.2f" % (label, confidence))
    return ret



def classify_pdf_image(jpg_file):
    """
    Apply image model to content image using tensorflow-serving.

    :param jpg_file: tmp jpg image file name, full path.
    :return: encoded confidence as type float with range [0.5,1.0] that example is positive
    """
    ret = 0.5  # lowest confidence encoded value
    img = cv2.imread(jpg_file).astype(np.float32)
    # we have 224x224, resize to 299x299 for shape (224, 224, 3)
    # ToDo: target size could vary, depending on the pre-trained model, should auto-adjust
    img299 = cv2.resize(img, dsize=(299, 299), interpolation=cv2.INTER_LINEAR)
    my_images = np.reshape(img299, (-1, 299, 299, 3))
    req_json = json.dumps({"signature_name": "serving_default", "instances": my_images.tolist()})
    try:
        response = requests.post(image_tf_server_url, data=req_json, headers=json_content_header)
        if response.status_code == 200:
            response_vec = response.json()["predictions"][0]
            confidence_other = response_vec[0]
            confidence_research = response_vec[1]
            log.debug("image classify %s  other=%.2f research=%.2f" % (jpg_file, confidence_other, confidence_research))
            if confidence_research > confidence_other:
                ret = encode_confidence("research", confidence_research)
            else:
                ret = encode_confidence("other", confidence_other)
    except Exception:
        log.warning("exception occurred processing REST tensorflow-serving for %s" % jpg_file)
    return ret


if __name__ == '__main__':
    """
    Apply the preprocessing to generate 
    """
    #  ToDo: process PDF files using all classifiers and create various confusion matrices to see where
    #     models agree/disagree. Data comes from directories associated with a defined category.
    #     REST api is not used.
    # init the arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_positive", type=str, default='',
                        help="dir. with positive PDF files to process, use a comma sep for multiple dirs",
                        required=True)
    parser.add_argument("--input_negative", type=str, default='',
                        help="dir. with negative PDF files to process, use a comma sep for multiple dirs",
                        required=True)
    parser.add_argument("--temp", type=str, default='/tmp', help="temp dir to use during extraction, /tmp default",
                        required=False)
    parser.add_argument("--skip", type=str, default='',
                        help="file containing file basenames to skip, one per line, optional", required=False)
    parser.add_argument("--testing", default=False, help="testing mode, be verbose, do only a few cycles",
                        action="store_true")

    # read arguments from the command line
    args = parser.parse_args()


