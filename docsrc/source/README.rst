
PhotoScript
===========

What is PhotoScript
-------------------

PhotoScript provides a python wrapper around Apple Photos applescript interface.  With PhotoScript you can interact with Photos using python.  Runs only on MacOS.  Tested on MacOS Catalina.

Installation
------------

PhotoScript uses setuptools, thus simply run:

``python3 setup.py install``

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

See Also
--------


* `osxphotos <https://github.com/RhetTbull/osxphotos>`_\ : Python package that provides read-only access to the Photos library including all associated metadata. 
