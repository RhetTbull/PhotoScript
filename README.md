# PhotoScript

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is PhotoScript

PhotoScript provides a python wrapper around Apple Photos applescript interface.  With PhotoScript you can interact with Photos using python.  Runs only on MacOS.  Tested on MacOS Catalina.

PhotosScript is limited by Photos' very limited AppleScript dictionary. 

## Installation

PhotoScript uses setuptools, thus simply run:

`python3 setup.py install`

Or you can install via pip:

`pip install photoscript`

## Example

```python
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
```

## Limitations
Photos' AppleScript interface is very limited.  For example, it cannot access information on faces in photos nor can it delete a photo.  PhotoScript is thus limited.  PhotoScript works by executing AppleScript through an Objective-C bridge from python.  Every method call has to do a python->Objective C->AppleScript round trip; this makes the interface much slower than native python code.  This is particularly noticeable when dealing with Folders which requires significant work arounds.

Where possible, PhotoScript attempts to provide work-arounds to Photos' limitations. For example, Photos does not provide a way to remove a photo from an album.  PhotoScript does provide a `Album.remove()` method but in order to do this, it creates a new album with the same name as the original, copies all but the removed photos to the new album then deletes the original album.  This simulates removing photos and produces the desired effect but is not the same thing as removing a photo from an album.

## Related Projects
- [osxphotos](https://github.com/RhetTbull/osxphotos): Python package that provides read-only access to the Photos library including all associated metadata. 
