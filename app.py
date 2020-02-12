#!/usr/bin/env python3

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


This is the Flask API definition.
"""

from flask import Flask
from flask import request, jsonify, abort
import html
import pdf_classifier
import url_classifier
import logging
import time

app = Flask(__name__)

logging.basicConfig(filename='research-pub.log', level=logging.DEBUG)
log = logging.getLogger(__name__)
log.info("STARTING   STARTING   STARTING   STARTING   STARTING   STARTING   STARTING")

@app.route('/', methods = ['GET'])
def toplevel():
    return "okay!"

@app.route('/api/list', methods = ['GET'])
def list_api():
    """
    Show the REST api.
    """
    # build HTML of the method list
    apilist = []
    rules = sorted(app.url_map.iter_rules(), key=lambda x: str(x))
    for rule in rules:
        f = app.view_functions[rule.endpoint]
        docs = f.__doc__ or ''

        # remove noisy OPTIONS
        methods = sorted([x for x in rule.methods if x != "OPTIONS"])
        url = html.escape(str(rule))
        apilist.append("<div><a href='{}'><b>{}</b></a> {}<br/>{}</div>".format(
            url, url, methods, docs))

    header = """<body>
        <style>
            body { width: 80%; margin: 20px auto;
                 font-family: Courier; }
            section { background: #eee; padding: 40px 20px;
                border: 1px dashed #aaa; }
        </style>
        <section>
        <h2>REST API (_COUNT_ end-points)</h2>
        """.replace('_COUNT_', str(len(apilist)))
    footer = "</section></body>"

    return header + "<br/>".join(apilist) + footer

@app.route('/classify/research-pub/url', methods = ['POST'])
def classify_by_url():
    """
    The given URL(s) is/are classified as referring to a research publication with a confidence value.
    A PDF under arxiv.org has a high confidence of being a research work.
    A PDF under amazon.com has a low confidence of being a research work.
    Parameter urls= in POST: json list of URLs like ["http://foo.com", "http://bar.com"]
    Each URL is separately classified.
    :return: json { "url1": 0.88, "url2": 0.92, "url3": 0.23 }
    """
    start_ts = int(time.time()*1000)
    input = request.json or {}
    url_list = input.get('urls')
    results_map = {}
    for url in url_list:
        confidence = url_classifier.classify_url(url)
        results_map[url] = confidence
    log.debug("results_map=%s" % (results_map))
    retmap = {"predictions": results_map}
    return jsonify(retmap)

@app.route('/classify/research-pub/<string:ctype>', methods = ['POST'])
def classify_pdf(ctype):
    """
    The given PDF is classified as a research publication or not. The PDF is not stored.
    params: "type" comma sep. list of { all, auto, image, bert, linear }
    :return: json
    """
    #log.debug("Request headers: %s" % (request.headers))
    log.debug("ctype=%s" % (ctype))
    if ctype is None:
        ctype = "auto"
    pdf_filestorage = request.files['pdf_content']
    log.debug("type=%s  pdf_content for %s" % (ctype, pdf_filestorage.filename))
    results = pdf_classifier.classify_pdf_multi(ctype, pdf_filestorage)
    dummy_reply = {"is_research" : 0.94,
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
    return jsonify(results), 200


if __name__ == '__main__':
    app.run(threaded=True)
