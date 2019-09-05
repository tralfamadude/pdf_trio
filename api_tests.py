#!/usr/bin/env python3
import json

import requests
import os
import json

API_HOSTPORT = os.environ.get('API_HOSTPORT')
if not API_HOSTPORT:
    raise ValueError('Missing api spec, define env var API_HOSTPORT=host:port')
API_HOST = API_HOSTPORT.split(":")[0]
API_PORT = API_HOSTPORT.split(":")[1]
API_BASE_URL = "http://%s:%s/" % (API_HOST, API_PORT)


headers = {"content-type": "application/json"}
url_map = {"urls": ["https://arxiv.org/pdf/1607.01759.pdf", "https://example.com/foo.pdf"]}
url_json = json.dumps(url_map)
json_response = requests.post(API_BASE_URL + "classify/research-pub/url", data=url_json, headers=headers)
if json_response is None:
    print("Response is None")
else:
    # expecting json like:   { "url1": 0.88, "url2": 0.23 }
    predictions = json.loads(json_response.text)['predictions']
