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

Also pytest if you want to run the tests.

To do this, you can create a venv and install within that.

See test.py for a wide range of examples.

Text Rendering
--------------

This library uses pycairo to render text as splines reduced to polylines. This means that non-single-line fonts (the vast majority) can be treated as shapes on a par with everything else.

This facilitates combining text with other shapes for fills.

It also allows transformations - these are applied at the (low) level of spline control points so should have high fidelity.

More generally, it means you don't need to use "Object to Path" in Inkscape to convert text to shapes.

Single-Line Fonts
-----------------

Single-line fonts are tricky to find, with most of the pages I've found attempting to list them ending in broken links.

However as of Feb2021, some reasonable ones are:

* CNC Vector: psfonts from http://philing.net/fonts.html
* CutlingsGeometric: http://cutlings.wasbo.net/single-line-fonts-options/
* CutlingsGeometricRound: http://cutlings.wasbo.net/single-line-fonts-options/
* HersheyScript1smooth: http://cutlings.wasbo.net/single-line-fonts-options/
* Stymie Hairline: https://fieldsofhether.blogspot.com/2017/11/6-single-line-fonts-that-will-write.html?m=1 (this has many other fonts too)
