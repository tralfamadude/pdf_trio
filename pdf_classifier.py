
import fasttext
from fasttext import load_model
import os
import argparse
import text_prep
import pdf_util
import logging

log = logging.getLogger(__name__)

version_map = {
    "image": "20190708",
    "linear": "20190720",
    "bert": "20190807",
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

def classify_pdf_multi(modes, pdf_content):
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
    :param pdf_content: raw PDF content (binary).
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
    tmp_pdf_name = pdf_util.write_tmp_file(pdf_content)
    # look ahead to see if text is required, so we can extract that now
    if ('linear' in mode_list) or ('bert' in mode_list) or ('auto' in mode_list):
        # extract text
        pdf_raw_text = pdf_util.extract_pdf_text(tmp_pdf_name)
        if len(pdf_raw_text) < 500:
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
            pdf_util.remove_tmp_file(jpg_file_page0)
    else:
        # apply named classifiers
        for classifier in mode_list:
            if classifier == "image":
                jpg_file_page0 = pdf_util.extract_pdf_image(tmp_pdf_name)
                # classify pdf_image_page0
                confidence_image = classify_pdf_image(jpg_file_page0)
                results[classifier] = confidence_image
                confidence_values.append(confidence_image)
                # remove tmp jpg
                pdf_util.remove_tmp_file(jpg_file_page0)
            elif classifier == "linear":
                if len(pdf_token_list) == 0:
                    # cannot use this classifier if no tokens extracted
                    continue  # skip
                confidence_linear = classify_pdf_linear(pdf_token_list)
                results[classifier] = confidence_linear
                confidence_values.append(confidence_linear)
            elif classifier == "bert":
                if len(pdf_token_list) == 0:
                    # cannot use this classifier if no tokens extracted
                    continue  # skip
                pdf_token_list_trimmed = text_prep.trim_tokens(pdf_token_list, 512)
                confidence_bert = classify_pdf_bert(pdf_token_list_trimmed)
                results[classifier] = confidence_bert
                confidence_values.append(confidence_bert)
            else:
                log.warning("ignoring unknown classifier ref: " + classifier)
    pdf_util.remove_tmp_file(tmp_pdf_name)
    #  compute 'is_research' using confidence_values
    confidence_overall = sum(confidence_values) / len(confidence_values)
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


def classify_pdf_bert(pdf_token_list):
    """
    Apply BERT model to content

    :param pdf_tokens: cleaned tokens list from pdf content
    :return: confidence as type float with range [0.0,1.0] that example is positive
    """
    #log.info("classify_pdf_bert: label=%s confidence=%.2f" % (label, confidence))
    return 0.599  # dummy


def classify_pdf_image(jpg_file):
    """
    Apply image model to content image

    :param jpg_file: tmp jpg image file name.
    :return: confidence as type float with range [0.0,1.0] that example is positive
    """
    #log.info("classify_pdf_image: label=%s confidence=%.2f" % (label, confidence))
    return 0.599  # dummy


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


