# Data Prep for FastText

[FastText](https://github.com/facebookresearch/fastText) is a type of linear classifier designed for high performance on large numbers of categories. 
Although we are only implementing a binary classifier, the fast C++ implementation works well with large
vocabularies and is easy to integrate for production. 

##        Overview
There are two training sets to be assembled for FastText in this project: PDF full text and URLs. 

The overall PDF processing script is `prep_all_fasttext.sh`

The PDF helper script  `prep_fasttext.sh` is used to prepare training data for FastText for one PDF file
at a time. 

The URL training examples are prepared by `process_tsv.py` which gets input from a tab-separated-value file. 
The tsv file is apt to be idiosyncratic to Internet Archive, so others using this project would need to adapt
or simply stub-out the URL classifier. 

##         Using FastText

### Required FastText Data Format
One sample per line, starting with stylized labels. There is no way to have an id for traceability.
Example:
```
__label__research word1 word2 word3 … 
__label__other word1 word2 word3 … 
...
```
where each line corresponds to one document.

### 

##        Full Text Classifier 

### Tokenizing
Tokenization happens in  `prep_fasttext.sh`.
Punctuation and EOL chars are converted to spaces, case is forced to lower case, control chars are converted to spaces. 
Consecutive spaces are converted to a single space.  
The remaining words, which are separated a space, are treated as tokens. 

### Details
We assemble this in stages. First an .ft file is created from each PDF document without an end of line character.
Then the page width and height which are found via pdfalto (driven by `pdf_to_xml_notext.sh`) then encoded into
tokens like `WIDTH450` and `HEIGHT650` are appended, and then an EOL char is appended to each .ft file.  

 ##       URL Classifier
 The goal of the URL classifier is to have a fast way to recognize whether a URL can be considered to be
 a likely research work. We know specific cases like this already: arxiv.org collects research paper preprints and
 any PDF found at that site is considered a research work. For the negative case, we know with great certainty
 that PDF files at irs.gov are not research works. 
 
 For this classifier to be useful, the confidence of positive
 classification must be very high. The implication of a negative classification is that the doc the URL points 
 to is unknown. 
 
