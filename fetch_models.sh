#!/usr/bin/env bash

# fetch model files!
mkdir -p model_snapshots
wget --recursive --no-clobber --no-parent --no-host-directories --cut-dirs=2 --reject "index.html*" --reject "robots.txt" --directory-prefix model_snapshots "https://archive.org/download/pdf_trio_models/"
