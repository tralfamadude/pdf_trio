#!/bin/bash
# demo of REST request using curl
curl localhost:3939/classify/research-pub/all -F pdf_content=@quick_test_samples/research/hidden-technical-debt-in-machine-learning-systems__2015.pdf
