#!/usr/bin/env python3 -i

# Open an interactive REPL with photoslib defined as PhotosLibrary
# useful for debugging or exploring the Photos database

# If you run this using python from command line, do so with -i flag:
# python3 -i examples/photos_repl.py

import photoscript

if __name__ == "__main__":
    photoslib = photoscript.PhotosLibrary()
    print(f"Photos version: {photoslib.version}")
    print("variables defined: photoslib")
