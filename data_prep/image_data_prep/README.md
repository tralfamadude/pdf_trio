# Image Classifier Fine-Tuning

Thumbnail images of the first page of the PDFs are used to fine-tune a pre-trained model. The Inception model 
has the highest accuracy. The images are generated from PDFs using ImageMagick (which uses ghostscript underneath) and
are sized to 224x224. During fine-tuning and at inference time, the image is resize to 299x299 which 
is what Inception uses. Since PDFs are not square, the images are created with white background padding. 

##         Preparation

Clone the tf_image_classifier companion repo, and set up the python env:
```
git clone git@git.archive.org:Baclace/tf_image_classifier.git
cd tf_image_classifier

conda create --name tf_hub python=3.7 
conda activate tf_hub
pip install -r requirements.txt
```

##          Create Images
Use this script to generate first page images from a directory of PDFs. 
```
./pdf_image.sh  pdf_dir dest_dir
```

##          Training
```
conda activate tf_hub
./train.sh training_data_dir
```
Where the training_data_dir has 2 subdirectories: research and other, which contain the prepared images.
