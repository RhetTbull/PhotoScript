""" Create new album and import photos """

import argparse
import pathlib

from photoscript import PhotosLibrary


def is_file(path):
    if pathlib.Path(path).is_file():
        return path
    else:
        raise argparse.ArgumentTypeError(f"is_file: {path} is not a valid file")


def main():
    parser = argparse.ArgumentParser(
        description="Import photos into Photos album. Create album if it doesn't exist. "
        "Does not check for duplicates."
    )
    parser.add_argument(
        "album", metavar="ALBUM", type=str, nargs=1, help="Album to import into"
    )
    parser.add_argument(
        "photo",
        metavar="PHOTO",
        type=is_file,
        nargs="+",
        help="Photos to import",
    )

    args = parser.parse_args()

    photoslib = PhotosLibrary()
    albums = photoslib.album_names()
    album_name = args.album[0]
    if album_name not in albums:
        print(f"Album {album_name} doesn't exist, creating it.")
        album = photoslib.create_album(album_name)
    else:
        album = photoslib.album(album_name)

    print(f"Importing {len(args.photo)} photos into album {album_name}.")
    photoslib.import_photos(args.photo, album=album_name, skip_duplicate_check=True)

    print(f"Done.  Album {album_name} now contains {len(album)} photos.")


if __name__ == "__main__":
    main()
