""" If run with python -m photoscript, drops user into interactive REPL """

from .__init__ import PhotosLibrary, Album, Folder, Photo

from code import InteractiveConsole

photoslib = PhotosLibrary()

def main():
    global photoslib
    banner = "PhotoScript REPL\n" \
            f"Photos version: {photoslib.version}\n" \
            f"Variables defined: photoslib"
    InteractiveConsole(locals=globals()).interact(banner=banner)

if __name__ == "__main__":
    main()