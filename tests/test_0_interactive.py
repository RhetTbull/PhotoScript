""" Tests which require user interaction to run """

from tests.photoscript_config_catalina import (
    ALBUM_1_PHOTO_EXPORT_FILENAMES,
    PHOTO_EXPORT_FILENAME_ORIGINAL,
)
import pytest
from applescript import AppleScript
from tests.conftest import photoslib, suspend_capture, get_os_version

OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import (
        ALBUM_1_NAME,
        ALBUM_1_UUID,
        ALBUM_NAMES_ALL,
        ALBUM_NAMES_TOP,
        FOLDER_NAME,
        FOLDER_NAMES_ALL,
        FOLDER_NAMES_TOP,
        FOLDER_UUID,
        IMPORT_PATHS,
        IMPORT_PHOTOS,
        NUM_PHOTOS,
        PHOTO_EXPORT_UUID,
        PHOTO_EXPORT_FILENAME,
        PHOTO_EXPORT_2_FILENAMES_ORIGINAL,
        PHOTO_EXPORT_2_FILENAMES,
        PHOTO_EXPORT_2_FILENAMES_ORIGINAL,
        PHOTO_FAVORITES_SET_UUID,
        PHOTO_FAVORITES_UNSET_UUID,
        PHOTOS_DICT,
        PHOTOS_FAVORITES,
        PHOTOS_FAVORITES_SET,
        PHOTOS_FILENAMES,
        PHOTOS_PLANTS,
        PHOTOS_UUID,
        PHOTOS_UUID_FILENAMES,
        SELECTION_UUIDS,
    )
else:
    pytest.exit("This test suite currently only runs on MacOS Catalina ")

########## Interactive tests run first ##########


def test_photoslibrary_import_photos_dup_check(photoslib):
    """ Attempt to import a duplicate photo with skip_duplicate_check = False
        This will cause Photos to display dialog box prompting user what to do """
    import os
    import pathlib

    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photoslib.import_photos(photo_paths)
    photos = [photo for photo in photoslib.photos()]
    assert len(photos) == NUM_PHOTOS + 1

    # Photos will block waiting for user to act on dialog box
    prompt = "Click Don't Import in Photos after the drop down sheet appears."
    os.system(f'say "{prompt}"')
    photos = photoslib.import_photos(photo_paths)
    assert not photos
    photos = [photo for photo in photoslib.photos()]
    assert len(photos) == NUM_PHOTOS + 1


def test_photoslibrary_selection(photoslib, suspend_capture):
    """ Test selection. NOTE: this test requires user interaction """
    import os
    import photoscript

    with suspend_capture:
        photoslib.activate
        prompt = (
            "In Photos, select the photo of the peppers "
            "and the photo with a face, then press Enter "
            "in this window."
        )
        os.system(f'say "{prompt}"')
        input(f"\n{prompt}")

    sel = photoslib.selection
    assert len(sel) == 2
    ids = [photo.id for photo in sel]
    assert sorted(ids) == sorted(SELECTION_UUIDS)


def test_album_spotlight(photoslib, suspend_capture):
    """ Test Album.spotlight() """
    import os

    with suspend_capture:
        album = photoslib.album("Farmers Market")
        album.spotlight()
        prompt = (
            "Press 'y' if the 'Farmers Market' album "
            "is spotlighted in Photos, otherwise press 'n' "
        )
        os.system(f'say "{prompt}"')
        answer = input(f"\n{prompt}")
        assert answer.lower() == "y"


def test_folder_spotlight(photoslib, suspend_capture):
    """ Test Folder.spotlight() """
    import os

    with suspend_capture:
        folder = photoslib.folder("Travel")
        folder.spotlight()
        prompt = (
            "Press 'y' if the 'Travel' folder "
            "is spotlighted in Photos, otherwise press 'n' "
        )
        os.system(f'say "{prompt}"')
        answer = input(f"\n{prompt}")
        assert answer.lower() == "y"


def test_photo_spotlight(photoslib, suspend_capture):
    """ Test Photo.spotlight() """
    import os

    with suspend_capture:
        photo = [photo for photo in photoslib.photos(uuid=[PHOTO_EXPORT_UUID])][0]
        photo.spotlight()
        prompt = (
            "Press 'y' if the photo of the peppers "
            "is spotlighted in Photos, otherwise press 'n' "
        )
        os.system(f'say "{prompt}"')
        answer = input(f"\n{prompt}")
        assert answer.lower() == "y"


def test_reset_photo_spotlight(photoslib, suspend_capture):
    """ Need to get back to Photos view for subsequent tests to work """
    import os

    with suspend_capture:
        prompt = "Select the 'Photos' view in Photos then press 'y'"
        os.system(f'say "{prompt}"')
        asnwer = input("\n{prompt}")
        assert answer.lower() == "y"


def test_album_export_photos_reveal_in_finder(photoslib, suspend_capture):
    import os
    import pathlib
    import tempfile

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")
    album = photoslib.album(ALBUM_1_NAME)
    album.export(tmpdir.name, reveal_in_finder=True)
    with suspend_capture:
        prompt = (
            f"Verify photos {ALBUM_1_PHOTO_EXPORT_FILENAMES} are revealed in the Finder "
            "by pressing 'y', otherwise, press 'n'."
        )
        os.system(f'say "{prompt}"')
        answer = input(f"\n{prompt}")
        assert answer.lower() == "y"


def test_photo_export_reveal_in_finder(photoslib, suspend_capture):
    import os
    import pathlib
    import tempfile
    import photoscript

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTOS_DICT[0]["uuid"])

    exported = photo.export(tmpdir.name, reveal_in_finder=True)
    exported = [pathlib.Path(filename).name for filename in exported]
    expected = [f"{pathlib.Path(PHOTOS_DICT[0]['filename']).stem}.jpeg"]
    assert exported == expected
    files = os.listdir(tmpdir.name)
    assert files == expected
    with suspend_capture:
        prompt = (
            f"Verify photo {exported} is revealed in Finder "
            "by pressing 'y', otherwise press 'n'."
        )
        os.system(f'say "{prompt}"')
        answer = input(f"\n{prompt}")
        assert answer.lower() == "y"

