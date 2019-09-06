#!/usr/bin/env python3
import json

import requests
import os
import json

API_BASE_URL = "http://localhost:3939/"

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
