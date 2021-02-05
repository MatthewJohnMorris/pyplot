pyplot
======

Use Python to generate SVG files for plotter art

Installation
------------

Just copy and use - no packaging as yet.

Usage
-----

You will need to have the following other packages installed 
* noise (for perlin stuff)
* pycairo (for text_width)
* opencv-python (for image reading and processing)
* svgwrite (for anything at all)

To do this, you can create a venv and install within that.

See test.py for a wide range of examples.

Single-Line Fonts
-----------------

Text-writing for plotter art works best (IMO) with single-line fonts. These are tricky to find, with most of the pages I've found attempting to list them ending in broken links.

However as of Feb2021, some reasonable ones are:

* CNC Vector: psfonts from http://philing.net/fonts.html
* CutlingsGeometric: http://cutlings.wasbo.net/single-line-fonts-options/
* CutlingsGeometricRound: http://cutlings.wasbo.net/single-line-fonts-options/
* HersheyScript1smooth: http://cutlings.wasbo.net/single-line-fonts-options/
* Stymie Hairline: https://fieldsofhether.blogspot.com/2017/11/6-single-line-fonts-that-will-write.html?m=1 (this has many other fonts too)

Note that to render these in a plot in Inkscape, you'll need to select everything and choose menu option "Path - Object To Path".