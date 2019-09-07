#!/usr/bin/env python3

from flask import Flask
from flask import request, jsonify, abort, render_template
import datetime
import json
import html
import config
from multiprocessing import Value
import pdf_classifier
import url_classifier
import logging
import time

"""

"""

classify_url_counter = Value('i', 0)
classify_pdf_counter = Value('i', 0)
classify_pdf_msec = Value('i', 0)
classify_url_msec = Value('i', 0)


app = Flask(__name__)

logging.basicConfig(filename='research-pub.log', level=logging.DEBUG)
log = logging.getLogger(__name__)
log.info("STARTING   STARTING   STARTING   STARTING   STARTING   STARTING   STARTING")

@app.route('/', methods = ['GET'])
def toplevel():
    # action can depend on run mode:  (needs to be set up somehow)
    #if config.IS_PRODUCTION:
    #    return report_stats()
    #if config.IS_LOCAL_DEV:
    #    return report_stats()
    return report_stats()

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
    # update counters
    with classify_url_counter.get_lock():
        classify_url_counter.value += 1
    finish_ts = int(time.time()*1000)
    with classify_url_msec.get_lock():
        classify_url_msec.value = classify_url_msec.value + finish_ts - start_ts
    return jsonify(retmap)

@app.route('/classify/research-pub/<string:ctype>', methods = ['POST'])
def classify_pdf(ctype):
    """
    The given PDF is classified as a research publication or not. The PDF is not stored.
    params: "type" comma sep. list of { all, auto, image, bert, linear }
    :return: json
    """
    start_ts = int(time.time() * 1000)
    log.debug("Request headers: %s" % (request.headers))
    # file_bytes = request.files  # ToDo: does this work?
    #type_param = request.form.get('type')
    log.debug("ctype=%s" % (ctype))
    pdf_content = request.files['pdf_content']
    if not pdf_content or len(pdf_content) == 0:
        log.error("no pdf content")
        return "", 500
    log.debug("type=%s  len(pdf_content)=%d" % (ctype, len(pdf_content)))
    results = pdf_classifier.classify_pdf_multi(ctype, pdf_content)
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
    # update counters
    with classify_pdf_counter.get_lock():
        classify_pdf_counter.value += 1
    finish_ts = int(time.time()*1000)
    with classify_pdf_msec.get_lock():
        classify_pdf_msec.value = classify_pdf_msec.value + finish_ts - start_ts
    return jsonify(results), 200

@app.route('/stats', methods = ['GET'])
def report_stats():
    """
    Show statistics from the current run of this service.
    :return:
    """
    local_classify_url_counter = 0
    local_classify_pdf_counter = 0
    local_classify_url_msec = 0
    local_classify_pdf_msec = 0

    with classify_url_counter.get_lock():
        local_classify_url_counter = classify_url_counter.value
    with classify_pdf_counter.get_lock():
        local_classify_pdf_counter = classify_pdf_counter.value
    with classify_url_msec.get_lock():
        local_classify_url_msec = classify_url_msec.value
    with classify_pdf_msec.get_lock():
        local_classify_pdf_msec = classify_pdf_msec.value

    # show stats
    return "url_classify_count={}\npdf_classify_count={}\nclassify_url_msec={}\nclassify_pdf_msec={}".\
        format(local_classify_url_counter, local_classify_pdf_counter, local_classify_url_msec, local_classify_pdf_msec)


if __name__ == '__main__':
    app.run(threaded=True)
