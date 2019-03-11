## Description

Simple python module to add handwritten signatures to pdf files in selected locations. In addition, date strings from handwritten numerals are automatically assembled and can equally be placed freely in the existing pdf.

___________________________________
<img src="doc/04.png" alt="example1" width="500" align="middle"/>
___________________________________

This is dockerized due to non-Python dependencies (ImageMagick) and the ambition to make it platform independent. However, the resulting docker image is somewhat bulky.


## Instructions

* Clone or download
* Replace the pdf files in the [signature](signature) and [numbers](numbers) folders (unless you are an obnoxious space-dictator; then feel free to just stick with the default signature). **Note:** 

<img src="doc/01.png" alt="example1" width="300" align="middle"/>


## Get high-quality signature pdfs

* Scan in whatever format
* Use gimp to convert to generate a transparency layer mask using the "Grayscale copy of layer" mode
* In gimp, invert the mask (Colors>Invert)
* Save as png file
* Use ImageMagick for transparency-conserving conversion to pdf: `convert -channel rgba -alpha on signature.png signature.pdf`

## Kudos

The `fancy_watermark.py` example of the marvellous [pdfrw](https://github.com/pmaupin/pdfrw) library served as a starting point for signpdf.

