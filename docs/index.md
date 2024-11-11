# Welcome to PhotoScript's Documentation

## Source Code

The source code for this project is available on [GitHub](https://github.com/RhetTbull/photoscript).

## What is PhotoScript

PhotoScript provides a python wrapper around Apple Photos applescript interface.  With PhotoScript you can interact with Photos using python.  Runs only on MacOS.  Tested on MacOS Catalina.

PhotosScript is limited by Photos' very limited AppleScript dictionary.

## Compatibility

Designed for MacOS Catalina/Photos 5.  Preliminary testing on Big Sur/Photos 6 beta shows this should work on Big Sur as well.  Photos' AppleScript interface has changed very little since Photos 2 (the earliest version I have access to).  This package should work with most versions of Photos but some methods may not function correctly on versions earlier than Photos 5.  If you find compatibility issues, open an issue or send a PR.

## Installation

You can install via pip:

`python3 -m pip install photoscript`

To install via the source code:

- Install [uv](https://github.com/astral-sh/uv) if not already installed
- Clone the repo: `git clone git@github.com:RhetTbull/PhotoScript.git`
- Change to the directory: `cd PhotoScript`
- Run `uv pip install -r pyproject.toml`.

If you want to develop code for PhotoScript, see [README_DEV.md](https://github.com/RhetTbull/PhotoScript/blob/master/README_DEV.md).

## Example

```python
""" Simple example showing use of photoscript """

import photoscript

photoslib = photoscript.PhotosLibrary()

photoslib.activate()
print(f"Running Photos version: {photoslib.version}")

album = photoslib.album("Album1")
photos = album.photos()

for photo in photos:
    photo.keywords = ["travel", "vacation"]
    print(f"{photo.title}, {photo.description}, {photo.keywords}")

new_album = photoslib.create_album("New Album")
photoslib.import_photos(["/Users/rhet/Downloads/test.jpeg"], album=new_album)

photoslib.quit()
```

## Documentation

Full documentation [here](https://rhettbull.github.io/PhotoScript/).

Additional documentation about Photos and AppleScript available on the [wiki](https://github.com/RhetTbull/PhotoScript/wiki/Welcome-to-the-PhotoScript-Wiki).

## Testing

Tested on MacOS Catalina, Photos 5 with 100% coverage.

## Limitations

Photos' AppleScript interface is very limited.  For example, it cannot access information on faces in photos nor can it delete a photo.  PhotoScript is thus limited.  PhotoScript works by executing AppleScript through an Objective-C bridge from python.  Every method call has to do a python->Objective C->AppleScript round trip; this makes the interface much slower than native python code.  This is particularly noticeable when dealing with Folders which requires significant work arounds.

Where possible, PhotoScript attempts to provide work-arounds to Photos' limitations. For example, Photos does not provide a way to remove a photo from an album.  PhotoScript does provide a `Album.remove()` method but in order to do this, it creates a new album with the same name as the original, copies all but the removed photos to the new album then deletes the original album.  This simulates removing photos and produces the desired effect but is not the same thing as removing a photo from an album.

## Related Projects

- [OSXPhotos](https://github.com/RhetTbull/osxphotos): Python app to work with pictures and associated metadata from Apple Photos on macOS. Also includes a package to provide programmatic access to the Photos library, pictures, and metadata.
- [PhotoKit](https://github.com/RhetTbull/photokit): Experimental Python package for accessing the macOS Photos.app library via Apple's native PhotoKit framework.


## Dependencies

- [py-applescript](https://github.com/rdhyee/py-applescript)
- [PyObjC](https://github.com/ronaldoussoren/pyobjc)
