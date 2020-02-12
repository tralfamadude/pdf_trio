# Data Prep

There are three kinds of classifiers used in this ensemble. Each is detailed in a subdirectory to describe
how data is prepared and how to train. 

* [FastText](ft_data_prep/README.md) a fast linear classifier
* [CNN](image_data_prep/README.md) convolutional neural network classifer 
* [BERT](bert_data_prep/README.md)

## Data Prep Tools

The external programs like imagemagick and pdftotext are used here and are also used by the REST API to 
prepare raw PDF content for inference.  

Processing individual PDFs using the scripts here will be straightforward. Some unavoidable idiosyncrasies creep in when
we process URL collections which are in an arbitrary .tsv file format. Inference by URL is completely separate
from classifying PDF content, however.  

### convert PDF to jpg
Run this in a directory containing .pdf files while specifying the destination directory to 
put the corresponding .jpg files. The files will have the same basename as the 
corresponding PDF.
```
./pdf_image.sh dest_jpg_dir
```
Images are 224x224 with a white background. The page image is horizontally centered and flush against the "north".
The regularization used for natural image training is not used because PDFs are not natural images. 

It was found empirically that a jpg size of 3000 or 
smaller is always blank. It would especially detrimental to have both positive and negatives examples that 
were blank, so these are removed. 

### Extract Text from PDFs
Running this will extract text from each .pdf to make the same basename plus .txt. 
Text is in human reading order. It relies on pdftotext and installation instructions are 
in the top level README file.   
```
./pdf_text.sh pdf_src_dir text_dest_dir 
```
If the text file size is too small (less than 500 bytes), it is removed to prevent training with 
insufficient features. If the txt file already exists, then that conversion is skipped. 

We found that pdftotext worked better than native python libraries for text extraction. 


