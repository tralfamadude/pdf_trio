#!/usr/bin/env python3
"""
Process pdf TAB URL info to make training data.
The input is a tsv file and assumes one .ft file per sample is destination of tokens.
This will append tokens from the tsv file to the .ft file. 
If the .ft file (one per doc ID) does not exist, it will be created
so that training data on just url metadata is possible. In the append case,
tokens from the pdf text have url metadata appended for a combined effect.

Example tsv row:
c487656070a636a24800776051e9d5449ebfbdea        https://core.ac.uk/download/pdf/81995083.pdf    201904150928

FastText needs a concatenation of .ft files to make a training
or testing set, to do that, add an EOL char to each .ft, concatentate all 
the .ft files from the categories (research, other, .etc) then sort -R to randomize order, then divide up into training and validation files.

Example url with archive.org prefix: https://web.archive.org/web/20180511040716/https://ekja.org/upload/pdf/kjae-57-444.pdf
The prefix is removed during processing.

"""
import argparse
import os
import pandas as pd

# init the arg parser
parser = argparse.ArgumentParser()
parser.add_argument("--category", type=str, default='', help="specify classification", required=True)
parser.add_argument("--input", type=str, default='', help="tsv file to process", required=True)
parser.add_argument("--working", type=str, default='', help="data dir for appending to category.ft file", required=True)
parser.add_argument("--domains", type=str, default='', help="optionally extract domains from tsv and store in given file")
parser.add_argument("--testing", default=False, help="testing mode, be verbose, only a few cycles", action="store_true")

# read arguments from the command line
args = parser.parse_args()

# get operands
target_category = args.category
infile = args.input
working_dir = args.working
print(" target_category=" + target_category)
print(" infile=" + infile)
print(" working_dir=" + working_dir)
print(" domains=" + args.domains)

# tsv file has:  ID URL [TS]
# no header
df_raw = pd.read_csv(infile, header=None, sep='\t')
# [0] is id (checksum)
# [1] is url, might have wayback prefix
# [2] is timestamp (or no col at all for some cases)

# In many cases, URL has prefix https://web.archive.org/web/20180725185648/ (where number varies)
# which should be removed to obtain the real URL. 

wayback_prefix = "https://web.archive.org/web/"

# remove wayback prefix and timestamp, if present
def remove_wayback_prefix(url):
    if url.startswith(wayback_prefix):
        url_no_prefix = url[len(wayback_prefix):]
        return url_no_prefix[url_no_prefix.find("/")+1:]
    return url

def remove_prefix(url, prefix):
    if url.startswith(prefix):
        url_no_prefix = url[len(prefix):]
        return url_no_prefix
    return url

def extract_domain(url):
    p = remove_prefix(url, "http://")
    p = remove_prefix(p, "https://")
    p = remove_prefix(p, "ftp://")
    p = p[:p.find("/")]
    offset_colon = p.find(":")
    if offset_colon > 1:
        return p[:offset_colon]
    return p

# return the URI part, but not the filename
def extract_uri(url):
    domain = extract_domain(url)
    url_no_domain = url[url.find(domain)+len(domain):]
    offset_colon = url_no_domain.find(":")
    if offset_colon == 0: 
        offset_slash = url_no_domain.find("/")
        url_no_domain = url_no_domain[offset_slash+1:]
    uri_no_file = url_no_domain[:url_no_domain.rfind('/')]
    offset_q = uri_no_file.find("?")
    if offset_q >= 0 :
        return uri_no_file[:offset_q]
    return uri_no_file

# returns a list of tokens from the url
# Note: some items are empty
def extract_tokens(url):
    d = extract_domain(url)
    uri = extract_uri(url)
    tokens = uri.split('/')
    tokens.append(d)
    return tokens

# convert a list of found tokens to a string of tokens each with a prefix
def gen_tokens(tlist):
    r = " U_".join(tlist)
    return r


if args.domains != '':
    # gather domains
    domains_list = [ extract_domain(remove_wayback_prefix(x)) for x in df_raw[1]]
    domains_list = list(set(domains_list))
    with open(args.domains, 'w') as f:
        for item in domains_list:
            f.write("%s\n" % item)


# normal processing
#  append to {id}.ft file if it exists, otherwise create the file
#
kount = 0
afile = working_dir + "/" + target_category + ".ft"
with open(afile, 'w') as f:
    for index, row in df_raw.iterrows():
        kount += 1
        if args.testing and kount > 5:
            print("Stopping early due to --testing flag")
            break
        url = str(row[1])
        tokens_string = gen_tokens(extract_tokens(remove_wayback_prefix(url)))
        if args.testing:
            print("testing: url={} afile={} tokens={}".format(url, afile, tokens_string))
        f.write("%s %s\n" % (("__label__"+target_category), tokens_string))
