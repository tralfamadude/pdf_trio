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


Basic tests for the API using defined sample data and whatever trained models are in effect.
This serves as a canonical examples for how to make requests.
"""

import os
from os import listdir
from os.path import isfile, join
import json

import requests

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


def test_all():
    #  ./tests/files/other and ./tests/files/research/
    negative_samples = collect_files("tests/files/other")
    print(negative_samples)
    positive_samples = collect_files("tests/files/research")
    print(positive_samples)
    for fname in negative_samples:
        do_classify_on_pdf(fname)
    for fname in positive_samples:
        do_classify_on_pdf(fname)

if __name__ == "__main__":
    test_all()
