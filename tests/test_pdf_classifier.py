
import os
import json
import pytest
import requests
from werkzeug.datastructures import FileStorage

from pdf_trio.pdf_classifier import PdfClassifier


def test_pdf_classifier_basics():
    c = PdfClassifier()

    test_pdf_path = 'tests/files/research/submission_363.pdf'

    # XXX:
    # {'outputs': [[0.000686553773, 0.999313474]]}

    for mode in ("linear", "bert", "image"):
        with open(test_pdf_path, 'rb') as f:
            pdf_fs = FileStorage(f)
            resp = c.classify_pdf_multi(mode, pdf_fs)
            print(resp)
            print(PdfClassifier.decode_confidence(resp[mode]))
            assert resp[mode] != 0.5
            assert resp['is_research'] != 0.5

    for mode in ("auto", "all"):
        with open(test_pdf_path, 'rb') as f:
            pdf_fs = FileStorage(f)
            resp = c.classify_pdf_multi(mode, pdf_fs)
            assert resp['is_research'] != 0.5

