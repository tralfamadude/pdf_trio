
"""
Copyright 2019 Internet Archive

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Classify whether a pdf is a research work based only on it's URL.
"""

import os
import logging

import fasttext
from fasttext import load_model

from pdf_trio import pdf_classifier

log = logging.getLogger(__name__)


class UrlClassifier:

    # In many cases, URL has prefix https://web.archive.org/web/20180725185648/
    # (where number varies) which should be removed to obtain the real URL.
    WAYBACK_PREFIX = "https://web.archive.org/web/"

    def __init__(self, **kwargs):

        model_path = os.environ.get('FT_URL_MODEL')
        if not model_path:
            raise ValueError('Missing fasttext model, define env var FT_URL_MODEL=full_path_to_basename')
        log.warning("Loading fasttext URL model...")
        self.fasttext_url_model = fasttext.load_model(model_path)

    @staticmethod
    def remove_wayback_prefix(url):
        """
        remove wayback prefix and timestamp, if present
        """
        if url.startswith(UrlClassifier.WAYBACK_PREFIX):
            url_no_prefix = url[len(UrlClassifier.WAYBACK_PREFIX):]
            return url_no_prefix[url_no_prefix.find("/")+1:]
        return url

    @staticmethod
    def remove_prefix(url, prefix):
        if url.startswith(prefix):
            url_no_prefix = url[len(prefix):]
            return url_no_prefix
        return url

    @staticmethod
    def extract_domain(url):
        p = UrlClassifier.remove_prefix(url, "http://")
        p = UrlClassifier.remove_prefix(p, "https://")
        p = UrlClassifier.remove_prefix(p, "ftp://")
        p = p[:p.find("/")]
        offset_colon = p.find(":")
        if offset_colon > 1:
            return p[:offset_colon]
        return p

    @staticmethod
    def extract_uri(url):
        """
        return the URI part, but not the filename
        """
        domain = UrlClassifier.extract_domain(url)
        url_no_domain = url[url.find(domain)+len(domain):]
        offset_colon = url_no_domain.find(":")
        if offset_colon == 0:
            offset_slash = url_no_domain.find("/")
            url_no_domain = url_no_domain[offset_slash+1:]
        uri_no_file = url_no_domain[:url_no_domain.rfind('/')]
        offset_q = uri_no_file.find("?")
        if offset_q >= 0:
            return uri_no_file[:offset_q]
        return uri_no_file


    @staticmethod
    def extract_url_tokens(url):
        """
        returns a list of tokens from the url
        Note: some items are empty
        """
        d = UrlClassifier.extract_domain(url)
        uri = UrlClassifier.extract_uri(url)
        tokens = uri.split('/')
        tokens.append(d)
        return tokens

    @staticmethod
    def gen_tokens(tlist):
        """
        convert a list of found tokens to a string of tokens each with a prefix
        """
        r = " U_".join(tlist)
        return r

    def classify_url(self, url):
        """
        :param url: one URL to classify
        :return: confidence [0.0,1.0] that url points to positive case
        """
        tokens_concat = UrlClassifier.gen_tokens(
            self.extract_url_tokens(self.remove_wayback_prefix(url)),
        )
        log.debug("classify_url: url=%s tokens=%s" % (url, tokens_concat))
        #  classify using fastText model for urlmeta
        results = self.fasttext_url_model.predict(tokens_concat)
        label = results[0][0]
        confidence = results[1][0]
        log.info("classify_url: label=%s confidence=%.2f url=%s" % (label, confidence, url))
        return pdf_classifier.PdfClassifier.encode_confidence(label, confidence)

