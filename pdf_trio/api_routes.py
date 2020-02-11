
import time
import logging

from flask import request, jsonify, abort, Blueprint

from pdf_trio import pdf_classifier, url_classifier


logging.basicConfig(filename='research-pub.log', level=logging.DEBUG)
log = logging.getLogger(__name__)
log.info("STARTING   STARTING   STARTING   STARTING   STARTING   STARTING   STARTING")


bp = Blueprint("classify", __name__)

bp.pdf_classifier = pdf_classifier.PdfClassifier()
bp.url_classifier = url_classifier.UrlClassifier()

@bp.route('/classify/research-pub/url', methods = ['POST'])
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
        confidence = bp.url_classifier.classify_url(url)
        results_map[url] = confidence
    log.debug("results_map=%s" % (results_map))
    retmap = {"predictions": results_map}
    return jsonify(retmap)

@bp.route('/classify/research-pub/<string:ctype>', methods = ['POST'])
def classify_pdf(ctype):
    """
    The given PDF is classified as a research publication or not. The PDF is not stored.
    params: "type" comma sep. list of { all, auto, image, bert, linear }
    :return: json

    Example result:

        {
          "is_research" : 0.94,
          "image" : 0.96,
          "linear" : 0.92,
          "bert" : 0.91,
          "version" : {
            "image" : "20190708",
            "linear" : "20190720",
            "bert" : "20190807",
            "urlmeta" : "20190722",
          }
        }
    """
    #log.debug("Request headers: %s" % (request.headers))
    log.debug("ctype=%s" % (ctype))
    if ctype is None:
        ctype = "auto"
    pdf_filestorage = request.files['pdf_content']
    log.debug("type=%s  pdf_content for %s" % (ctype, pdf_filestorage.filename))
    results = bp.pdf_classifier.classify_pdf_multi(ctype, pdf_filestorage)
    return jsonify(results), 200

