""" Test Photo class """

from tests.photoscript_config_catalina import PHOTO_EXPORT_FILENAME_ORIGINAL
import pytest
from applescript import AppleScript
from tests.conftest import photoslib, suspend_capture, get_os_version

OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import (
        PHOTOS_DICT,
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


def test_photo_init_uuid_id(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert isinstance(photo_obj, photoscript.Photo)
        assert photo_obj.id == photo["uuid"]
        assert photo_obj.uuid == photo["uuid_osxphotos"]


def test_photo_name(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.name == photo["title"]
        assert photo_obj.title == photo["title"]

        # set name
        photo_obj.name = "New Name"
        assert photo_obj.name == "New Name"
        assert photo_obj.title == "New Name"

        # set title
        photo_obj.title = "New Title"
        assert photo_obj.name == "New Title"
        assert photo_obj.title == "New Title"

        # clear name
        photo_obj.name = None
        assert photo_obj.name is None
        assert photo_obj.title is None

        # clear title
        photo_obj.title = None
        assert photo_obj.name is None
        assert photo_obj.title is None


def test_photo_description(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.description == photo["description"]
        photo_obj.description = "New Description"
        assert photo_obj.description == "New Description"
        photo_obj.description = None
        assert photo_obj.description is None


def test_photo_keywords(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.keywords == photo["keywords"]
        photo_obj.keywords = ["Foo", "Bar"]
        assert sorted(photo_obj.keywords) == sorted(["Foo", "Bar"])
        photo_obj.keywords = []
        assert photo_obj.keywords == []
