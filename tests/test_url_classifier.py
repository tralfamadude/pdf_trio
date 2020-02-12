
from pdf_trio.url_classifier import UrlClassifier


def test_url_extract():
    u = UrlClassifier()

    bare = u.remove_wayback_prefix("https://web.archive.org/web/20200102030405/http://fatcat.wiki/one.pdf")
    assert bare == "http://fatcat.wiki/one.pdf"
    domain = u.extract_domain(bare)
    assert domain == "fatcat.wiki"

def test_url_classify():

    u = UrlClassifier()
    resp = u.classify_url("https://web.archive.org/web/20200102030405/http://fatcat.wiki/one.pdf")
    assert type(resp) == float
    assert resp != 0.5
