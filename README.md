## Description

Simple python module to add handwritten signatures to pdf files in selected locations. In addition, date strings from handwritten numerals are automatically assembled and can equally be placed freely in the existing pdf.

___________________________________
<img src="doc/04.png" alt="example1" width="500" align="middle"/>

______________________________________

This is dockerized due to non-Python dependencies (ImageMagick) and the ambition to make it platform independent. However, the resulting docker image is somewhat bulky.


## Instructions
### Setup

* Clone or download
* Replace the pdf files in the [signature](signature) and [numbers](numbers) folders (unless you are an obnoxious space-dictator; then feel free to just stick with the default signature). **Note:** To avoid repetition of the handwritten numerals in the date string, multiple files can be provided for each number (for example [3_1.pdf](numbers/3_1.pdf), [3_2.pdf](numbers/3_2.pdf), and [3_3.pdf](numbers/3_3.pdf) for the numeral 3). The exact number of files per numeral is flexible and only affects the esthetics of the result. The files [s_1.pdf](numbers/s_1.pdf) etc are the date string separators. They are slashes in the example case but could be any other symbol (still with filenames "s_*").

### Usage
* Copy the target pdf file to the root directory, replacing the *example_document.pdf*. For predictable behavior, only one pdf file should be in the root directory at any time, unless its filename ends with *_signed.pdf* (in which case it is the output document). Needless to say that input documents must not have filenames *\*_signed.pdf* 
* Fire up docker-compose.
* Open [http://localhost:5006/app](http://localhost:5006/app) in a browser.
* An empty 

<img src="doc/01.png" alt="example1" width="300" align="middle"/>


## Get high-quality signature pdfs

* Scan in whatever format
* Use gimp to convert to generate a transparency layer mask using the "Grayscale copy of layer" mode
* In gimp, invert the mask (Colors>Invert)
* Save as png file
* Use ImageMagick for transparency-conserving conversion to pdf: `convert -channel rgba -alpha on signature.png signature.pdf`

## Kudos

The `fancy_watermark.py` example of the marvellous [pdfrw](https://github.com/pmaupin/pdfrw) library served as a starting point for signpdf.

