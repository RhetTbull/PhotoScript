""" Create a new test library in Photos """

import os
import pathlib
import sys
from collections import namedtuple 

import photoscript

ALBUMS = [
    {"folder": None, "album": "Empty Album"},
    {"folder": None, "album": "Farmers Market"},
    {"folder": ["Travel"], "album": "San Juan Capistrano"},
]
FOLDERS = [["Folder1", "SubFolder1"]]
PhotoTuple = namedtuple("PhotoTuple", "path favorite keywords album")
PHOTOS = [
    PhotoTuple("tests/test_images/IMG_0096.jpeg", False, [], []),
    PhotoTuple("tests/test_images/IMG_2242.JPG", False, [], []),
    PhotoTuple("tests/test_images/IMG_2510.JPG", True, [], [[], "Farmers Market"]),
    PhotoTuple(
        "tests/test_images/IMG_2768.JPG", True, [], [["Travel"], "San Juan Capistrano"]
    ),
    PhotoTuple(
        "tests/test_images/IMG_2774.JPG",
        False,
        ["travel"],
        [["Travel"], "San Juan Capistrano"],
    ),
]
library_name = ""
while library_name == "":
    library_name = input(
        "Create a new library in Photos then type name of library here: "
    )

photoslib = photoscript.PhotosLibrary()
if len(photoslib):
    sys.exit("Photo library doesn't appear to be empty.")

print("Creating folders:")
for folder in FOLDERS:
    print(folder)
    photoslib.make_folders(folder)

print("Creating albums:")
for album in ALBUMS:
    print(f"{album['folder']}, {album['album']}")
    if album["folder"] is not None:
        photoslib.make_album_folders(album["album"], album["folder"])
    else:
        photoslib.create_album(album["album"])

print("Adding Photos:")
cwd = os.getcwd()
for photo in PHOTOS:
    photo_path = pathlib.Path(cwd) / photo.path
    print(f"{photo_path}")
    if photo.album and photo.album[0]:
        # album in a folder
        album = photoslib.make_album_folders(photo.album[1], photo.album[0])
    elif photo.album:
        # no folder
        album = photoslib.album(photo.album[1])
        if album is None:
            album = photoslib.create_album(photo.album[1])
    else:
        album = None
    imported = photoslib.import_photos([photo_path], album=album)
    if len(imported) != 1:
        sys.exit(f"Something went wrong with import of {photo_path}")
    else:
        imported = imported[0]
    imported.favorite = photo.favorite
    imported.keywords = photo.keywords

print("Done!")
print("Folders:")
folders = photoslib.folders(top_level=False)
for folder in folders:
    print(f"{folder.path_str()}: {folder.id}")

print("Albums:")
albums = photoslib.albums(top_level=False)
for album in albums:
    print(f"{album.path_str()}: {album.id}")

print("Photos:")
photos = photoslib.photos()
for photo in photos:
    print(f"{photo.filename}, {photo.favorite}, {photo.keywords}: {photo.id}")
