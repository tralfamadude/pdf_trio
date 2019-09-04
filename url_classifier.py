"""
Classify whether a pdf is a research work based only on it's URL.
"""

import fasttext
from fasttext import load_model
import os
import glob
import re
import logging
import pdf_classifier

log = logging.getLogger("url_classifier")

FT_URL_MODEL = os.environ.get('FT_URL_MODEL')
if not FT_URL_MODEL:
    raise ValueError('Missing fasttext model, define env var FT_URL_MODEL=full_path_to_basename')
fasttext_url_model = fasttext.load_model(FT_URL_MODEL)

# In many cases, URL has prefix https://web.archive.org/web/20180725185648/ (where number varies)
# which should be removed to obtain the real URL.

wayback_prefix = "https://web.archive.org/web/"

# remove wayback prefix and timestamp, if present
def remove_wayback_prefix(url):
    if url.startswith(wayback_prefix):
        url_no_prefix = url[len(wayback_prefix):]
        return url_no_prefix[url_no_prefix.find("/")+1:]
    return url


def remove_prefix(url, prefix):
    if url.startswith(prefix):
        url_no_prefix = url[len(prefix):]
        return url_no_prefix
    return url


def extract_domain(url):
    p = remove_prefix(url, "http://")
    p = remove_prefix(p, "https://")
    p = remove_prefix(p, "ftp://")
    p = p[:p.find("/")]
    offset_colon = p.find(":")
    if offset_colon > 1:
        return p[:offset_colon]
    return p


# return the URI part, but not the filename
def extract_uri(url):
    domain = extract_domain(url)
    url_no_domain = url[url.find(domain)+len(domain):]
    offset_colon = url_no_domain.find(":")
    if offset_colon == 0:
        offset_slash = url_no_domain.find("/")
        url_no_domain = url_no_domain[offset_slash+1:]
    uri_no_file = url_no_domain[:url_no_domain.rfind('/')]
    offset_q = uri_no_file.find("?")
    if offset_q >= 0 :
        return uri_no_file[:offset_q]
    return uri_no_file


# returns a list of tokens from the url
# Note: some items are empty
def extract_tokens(url):
    d = extract_domain(url)
    uri = extract_uri(url)
    tokens = uri.split('/')
    tokens.append(d)
    return tokens


# convert a list of found tokens to a string of tokens each with a prefix
def gen_tokens(tlist):
    r = " U_".join(tlist)
    return r

def classify_url(url):
    """
    :param url: one URL to classify
    :return: confidence [0.0,1.0] that url points to positive case
    """
    tokens = gen_tokens(extract_tokens(remove_wayback_prefix(url)))
    #  classify using fastText model for urlmeta
    results = fasttext_url_model.predict(" ".join(tokens))
    label = results[0][0]
    confidence = results[1][0]
    log.info("classify_url: label=%s confidence=%.2f url=%s" % (label, confidence, url))
    return pdf_classifier.encode_confidence(label, confidence)
