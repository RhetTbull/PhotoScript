""" Test Photo class """

from tests.photoscript_config_catalina import PHOTO_EXPORT_FILENAME_ORIGINAL
import pytest
from applescript import AppleScript
from tests.conftest import photoslib, suspend_capture, get_os_version

OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import PHOTOS_DICT
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


def test_photo_favorite(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.favorite == photo["favorite"]
        photo_obj.favorite = not photo["favorite"]
        assert photo_obj.favorite != photo["favorite"]


def test_photo_height_width(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.height == photo["height"]
        assert photo_obj.width == photo["width"]


def test_photo_altitude(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.altitude == photo["altitude"]


def test_photo_location(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        lat, lon = photo_obj.location
        assert (lat, lon) == photo["location"]
        photo_obj.location = (34.0, -118.0)
        assert photo_obj.location == (34.0, -118.0)
        photo_obj.location = (None, None)
        assert photo_obj.location == (None, None)


def test_photo_date(photoslib):
    import datetime
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        date = datetime.datetime.fromisoformat(photo["date"])
        assert photo_obj.date == date
        photo_obj.date = datetime.datetime(2020, 9, 14)
        assert photo_obj.date == datetime.datetime(2020, 9, 14)


def test_photo_filename(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.filename == photo["filename"]


def test_photo_export_basic(photoslib):
    import os
    import pathlib
    import tempfile
    import photoscript

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTOS_DICT[0]["uuid"])

    exported = photo.export(tmpdir.name)
    exported = [pathlib.Path(filename).name for filename in exported]
    expected = [f"{pathlib.Path(PHOTOS_DICT[0]['filename']).stem}.jpeg"]
    assert exported == expected
    files = os.listdir(tmpdir.name)
    assert files == expected


def test_export_photo_original_duplicate_overwrite(photoslib):
    """ Test calling export twice resulting in 
        duplicate filenames but use overwrite = true"""
    import os
    import pathlib
    import tempfile
    import photoscript

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTOS_DICT[0]["uuid"])
    exported1 = photo.export(tmpdir.name, original=True)
    exported2 = photo.export(tmpdir.name, original=True, overwrite=True)
    exported = list({pathlib.Path(filename).name for filename in exported1 + exported2})

    expected = [f"{pathlib.Path(PHOTOS_DICT[0]['filename']).stem}.jpeg"]
    assert exported == expected
    files = os.listdir(tmpdir.name)
    assert files == expected


def test_photo_duplicate(photoslib):
    import photoscript

    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        new_photo = photo_obj.duplicate()
        assert isinstance(new_photo, photoscript.Photo)
        assert new_photo.filename == photo_obj.filename
