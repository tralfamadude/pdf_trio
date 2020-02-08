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



Process pdf txt files to make training data for BERT to use run_classifier.py which comes with the
repo https://github.com/google-research/bert 

The output is a TSV file for one category. Multiple TSV files (for positive/negative cases) can be concatenated 
and should be shuf'ed.
 
The inputs are txt files which came from PDFs, organized in a single directory.

The text is cleaned up to remove punctuation, control chars, and truncated in the middle if the number 
of words exceeds the specified max. 
"""
import argparse
import os
import glob
import re


# init the arg parser
parser = argparse.ArgumentParser()
parser.add_argument("--category", type=str, default='', help="specify classification, 0 or 1", required=True)
parser.add_argument("--input", type=str, default='', help="directory with .txt files to process", required=True)
parser.add_argument("--output", type=str, default='', help="the output tsv file", required=True)
parser.add_argument("--max_tokens", type=int, default=512, help="max tokens")
parser.add_argument("--testing", default=False, help="testing mode, be verbose, only a few cycles", action="store_true")

# remove these:  working  domains append_only
parser.add_argument("--append_only", default=False, help="only append to existing .ft files", action="store_true")

# read arguments from the command line
args = parser.parse_args()

# get operands
target_category = args.category
indir = args.input
outfile = args.output

print(" target_category=" + target_category)
print(" indir=" + indir)

""" 
Output Format is TSV

column 1 - a unique ID
column 2 - an integer label - my dataset uses 0 for a negative paper and 1 for a positive paper
column 3 - a dummy column where each line has the same letter (in this case 'a') - perhaps this is used in other NLP tasks
column 4 - the text, which has had tabs and newlines stripped out of it.
"""


# returns a list of tokens from the url
# Note: some items are empty
def extract_tokens(url):
    d = extract_domain(url)
    uri = extract_uri(url)
    tokens = uri.split('/')
    tokens.append(d)
    return tokens

def basename(fpath):
    offset_slash = fpath.rfind("/")
    if offset_slash >= 0:
        fpath = fpath[offset_slash+1:]
    return fpath

def dirname(fpath):
    offset_slash = fpath.rfind("/")
    if offset_slash <= 0:
        return "."
    fpath = fpath[:offset_slash]
    return fpath

def trim_tokens(file_tokens):
    ntokens = len(file_tokens)
    if ntokens > args.max_tokens:
        cut_out = ntokens - args.max_tokens
        front_end_offset = int(args.max_tokens/2)
        back_begin_offset = front_end_offset + cut_out
        file_tokens = file_tokens[:front_end_offset] + file_tokens[back_begin_offset:]
    return file_tokens


kount = 0

with open(outfile, 'w') as fout:
    for filename in glob.glob(indir + "/*.txt"):
        kount += 1
        if args.testing and kount > 5: 
            print("Stopping early due to --testing flag")
            break;
        fid = basename(filename[:-4])
        with open(filename, 'r') as file:
            file_text = file.read()
            file_text = re.sub(r'[\x00-\x1F]+', ' ', file_text)
            # ToDo: should really use unicode char groupings to clean 
            file_text = file_text.replace(',', ' ')
            file_text = file_text.replace('.', ' ')
            file_text = file_text.replace('!', ' ')
            file_text = file_text.replace(';', ' ')
            file_text = file_text.replace('-', ' ')
            file_text = file_text.replace('"', ' ')
            file_text = file_text.replace("'", ' ')
            file_text = file_text.replace("(", ' ')
            file_text = file_text.replace(")", ' ')
            file_text = file_text.replace("[", ' ')
            file_text = file_text.replace("]", ' ')
            file_text = file_text.replace("/", ' ')
            # convert consecutive whitespace to one space
            file_text = re.sub('\s+', ' ', file_text)
            file_tokens = trim_tokens(file_text.split())
            fout.write("%s\t%s\ta\t%s\n" % (fid, target_category, " ".join(file_tokens)))


