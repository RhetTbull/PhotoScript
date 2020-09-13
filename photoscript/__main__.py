""" If run with python -m photoscript, drops user into interactive REPL """

from .__init__ import PhotosLibrary, Album, Folder, Photo

from code import InteractiveConsole

if __name__ == "__main__":
    photoslib = PhotosLibrary()

    banner = "PhotoScript REPL\n" \
            f"Photos version: {photoslib.version}\n" \
            f"Variables defined: photoslib"
    scope_vars = {"photoslib": photoslib}
    InteractiveConsole(locals=globals()).interact(banner=banner)
