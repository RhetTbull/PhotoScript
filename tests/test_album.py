""" Test Album class """

import pytest
from applescript import AppleScript
from tests.conftest import photoslib, suspend_capture, get_os_version


OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import (
        ALBUM_1_NAME,
        ALBUM_1_UUID,
        ALBUM_1_UUID_OSXPHOTOS,
        ALBUM_NAMES_ALL,
        ALBUM_NAMES_TOP,
        FOLDER_NAME,
        FOLDER_NAMES_ALL,
        FOLDER_NAMES_TOP,
        FOLDER_UUID,
        IMPORT_PATHS,
        IMPORT_PHOTOS,
        NUM_PHOTOS,
        PHOTO_FAVORITES_SET_UUID,
        PHOTO_FAVORITES_UNSET_UUID,
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

########## Non-interactive tests ##########


def test_album_init():
    import photoscript

    album = photoscript.Album(ALBUM_1_UUID)
    assert isinstance(album, photoscript.Album)


def test_album_init_bad_uuid():
    import photoscript

    with pytest.raises(ValueError):
        assert photoscript.Album("BAD_UUID")


def test_album_id():
    import photoscript

    album = photoscript.Album(ALBUM_1_UUID)
    assert album.uuid == ALBUM_1_UUID


def test_album_uuid():
    import photoscript

    album = photoscript.Album(ALBUM_1_UUID)
    assert album.uuid == ALBUM_1_UUID_OSXPHOTOS


