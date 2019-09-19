#!/usr/bin/env python3

"""
Basic tests for the API using defined sample data and whatever trained models are in effect.
This serves as a canonical examples for how to make requests.
"""

import json
import requests
import os
import json
from os import listdir
from os.path import isfile, join

API_BASE_URL = "http://localhost:3939/"

#
#    Test Classify By URL
#
headers = {"content-type": "application/json"}
url_map = {"urls": ["https://arxiv.org/pdf/1607.01759.pdf", "https://example.com/maps/foo.pdf"]}
url_json = json.dumps(url_map)
json_response = requests.post(API_BASE_URL + "classify/research-pub/url", data=url_json, headers=headers)
if json_response is None:
    print("Response is None")
else:
    # expecting json like:   { "url1": 0.88, "url2": 0.23 }
    print("verbatim response=%s" % (json_response.text))
    predictions = json.loads(json_response.text)["predictions"]
    for k in predictions:
        print("%.2f : %s" % (predictions[k], k))


#
#    Test Linear Classify of a PDF
#
# read in sample pdf one at a time and classify them

def do_classify_on_pdf(pdf_file_path):
    target_url = API_BASE_URL + "classify/research-pub/all"
    print("-----")
    print("process %s" % (pdf_file_path))
    with open(pdf_file_path, 'rb') as f:
        filename = os.path.basename(pdf_file_path)
        form_data = {
            "pdf_content": (filename, f, "application/octet-stream")
        }
        response = requests.post(target_url, files=form_data)
    # print(response.headers)  # DEBUG
    print("%s  %s" % (response.text, pdf_file_path))  # DEBUG


def collect_files(dir_path):
    ret_list = []
    for fname in listdir(dir_path):
        fname_full = dir_path + "/" + fname
        if isfile(fname_full):
            ret_list.append(fname_full)
    return ret_list


#  ./quick_test_samples/other and ./quick_test_samples/research/
negative_samples = collect_files("quick_test_samples/other")
print(negative_samples)
positive_samples = collect_files("quick_test_samples/research")
print(positive_samples)
for fname in negative_samples:
    do_classify_on_pdf(fname)
for fname in positive_samples:
    do_classify_on_pdf(fname)
