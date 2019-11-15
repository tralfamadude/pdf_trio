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

The full text dataset is prepared by the script `prep_all_fasttext.sh`
```
./prep_all_fasttext.sh
Usage:  basename_for_dataset dest_dir other_pdfs_dir research_pdfs_dir_1 [research_pdfs_dir_2]
```

The linux executable `pdftotext` is required; instructions for that installation are in the top level README.  
We found that `pdftotext` worked more often than python packages for PDF text extraction.  

Example creation of training data:
```
./prep_all_fasttext.sh ft20191001 dataset_dir/ /srv/other_pdfs /srv/research_pdfs  
```
where the first arg is a basename used in generated files and as a directory name; think of this as the name of a session
that encompasses the dataset and training. The `dataset_dir/` arg is a directory where to create
a subdirectory (`dataset_dir/ft20191001/`) to put generated files.  

A sub-subdirectory called staging/ is created to hold .ft files, one for each PDF for
which text could be extracted. These staging files and directory can be deleted after `prep_all_fasttext.sh` is run; 
they are useful for inspecting extracted text because the training file itself does not contain doc IDs. 
The staging directory is emptied at the start of a run. 

Speed: about 6 docs are processed per second. 

Then do FastText training and evaluation example:
```
./train.sh ft20191001 dataset_dir/ /my/path/to/fasttext
```
The basename_for_dataset, dataset_dir, and path to the fastText directory are specified. Training and 
evaluation only takes about a minute. 

The result will be something like:
```
ls dataset_dir/ft20191001/
ftft20191001.bin
ftft20191001.samples
ftft20191001.samples.train
ftft20191001.samples.validate
ftft20191001.vec
```
where the training step added the .vec and .bin files.

### Tokenizing
Tokenization happens in  `prep_fasttext.sh`.
Punctuation and EOL chars are converted to spaces, case is forced to lower case, control chars are converted to spaces. 
Consecutive spaces are converted to a single space.  
The remaining words, which are separated a space, are treated as tokens. 


 ##                 URL Classifier
 The goal of the URL classifier is to have a fast way to recognize whether a URL can be considered to be
 a likely research work. We know specific cases like this already: arxiv.org collects research paper preprints and
 any PDF found at that site is considered a research work. For the negative case, we know with great certainty
 that PDF files at irs.gov are not research works. 
 
 For this classifier to be useful, the confidence of positive
 classification must be very high. The implication of a negative classification is that the doc the URL points 
 to is unknown. 
 
### Create URL Dataset 

The URL dataset is prepared by the script `prep_all_url_fasttext.sh`
```
./prep_all_url_fasttext.sh
Usage:  basename_for_dataset dest_dir input_tsv_other input_tsv_research
```

Example creation of URL dataset:
```
./prep_all_url_fasttext.sh u20191001 dest_dir/  other.tsv research.tsv
```
_Do not use the same dest dir as for the full text._

Then do FastText URL training and evaluation example:
```
./train.sh u20191001 url_dataset_dir/ /my/path/to/fasttext
```
The basename_for_dataset, dataset_dir, and path to the fastText directory are specified. Training and 
evaluation only takes about a minute. 
