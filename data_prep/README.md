# Data Prep

Scripts for training data preparation are here.
The external programs like imagemagick and pdftotext are used here and are also used by the REST API to 
prepare raw PDF content for inference.  

Processing individual PDFs using the scripts here will be straightforward. Some unavoidable idiosyncrasies creep in when
we process URL collections which are in an arbitrary .tsv file format. Inference by URL is completely separate
from classifying PDF content, however.  

## convert PDF to jpg
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
were blank. 

## Obtain PDF page size
Using pdfalto (a bundled binary), the width and height of the PDF pages can be extracted:
```
./pdf_to_xml_notext.sh  file.pdf  target_dir
``` 
The corresponding file basename plus extension .xmlnt ("xml no text") is saved in the target directory.
The output file contains the width and height of the first page like `WIDTH450` and `HEIGHT650`; we have some 
indication that the page dimensions are helpful in discerning research works. 

## Extract Text from PDFs
Running this will extract text from each .pdf to make the same basename plus .txt. 
Text is in human reading order. It relies on pdftotext and installation instructions are 
in the top level README file.   
```
./pdf_dir_text.sh pdf_src_dir text_dest_dir 
```
If the text file size is too small (less than 500 bytes), it is removed to prevent training with 
insufficient features. If the txt file already exists, then that conversion is skipped. 


