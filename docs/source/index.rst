.. PhotoScript documentation master file, created by
   sphinx-quickstart on Sat Aug 15 16:29:13 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PhotoScript's documentation!
=======================================

What is PhotoScript
-------------------

PhotoScript provides a python wrapper around Apple Photos applescript interface.  With PhotoScript you can interact with Photos using python.  Runs only on MacOS.  Tested on MacOS Catalina.

Installation
------------

PhotoScript uses setuptools, thus simply run:

`python3 setup.py install`

Example
-------

.. code-block:: python

   """ Simple example showing use of photoscript """

   import photoscript

   photoslib = photoscript.PhotosLibrary()

   photoslib.activate()
   print(f"Running Photos version: {photoslib.version}")

   album = photoslib.album("Album1")
   photos = album.photos

   for photo in photos:
      print(f"{photo.title}, {photo.description}, {photo.keywords}")

   new_album = photoslib.create_album("New Album")
   photoslib.import_photos(["/Users/rhet/Downloads/test.jpeg"], album=new_album)

   photoslib.quit()

Documentation
=============

.. toctree::
   :maxdepth: 3

   reference



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
