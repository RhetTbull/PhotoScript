""" Test Photo class """

import datetime
import os
import pathlib
import tempfile

import pytest
from applescript import AppleScript

import photoscript
from tests.conftest import photoslib, suspend_capture
from tests.photoscript_config_data import PHOTO_EXPORT_FILENAME_ORIGINAL, PHOTOS_DICT
from tests.utils import stemset

from .datetime_utils import datetime_remove_tz, datetime_to_new_tz, get_local_tz

########## Interactive tests run first ##########


########## Non-interactive tests ##########


def test_photo_init_uuid_id(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert isinstance(photo_obj, photoscript.Photo)
        assert photo_obj.id == photo["uuid"]
        assert photo_obj.uuid == photo["uuid_osxphotos"]


def test_photo_init_uuid_osxphotos(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid_osxphotos"])
        assert isinstance(photo_obj, photoscript.Photo)
        assert photo_obj.id == photo["uuid"]
        assert photo_obj.uuid == photo["uuid_osxphotos"]


def test_photo_init_bad_uuid(photoslib: photoscript.PhotosLibrary):
    with pytest.raises(ValueError):
        photoscript.Photo("BAD_UUID")


def test_photo_name(photoslib: photoscript.PhotosLibrary):
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
        assert photo_obj.name == ""
        assert photo_obj.title == ""

        # clear title
        photo_obj.title = None
        assert photo_obj.name == ""
        assert photo_obj.title == ""


def test_photo_description(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.description == photo["description"]
        photo_obj.description = "New Description"
        assert photo_obj.description == "New Description"
        photo_obj.description = None
        assert photo_obj.description == ""


def test_photo_keywords(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.keywords == photo["keywords"]
        photo_obj.keywords = ["Foo", "Bar"]
        assert sorted(photo_obj.keywords) == sorted(["Foo", "Bar"])
        photo_obj.keywords = []
        assert photo_obj.keywords == []


def test_photo_favorite(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.favorite == photo["favorite"]
        photo_obj.favorite = not photo["favorite"]
        assert photo_obj.favorite != photo["favorite"]


def test_photo_height_width(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.height == photo["height"]
        assert photo_obj.width == photo["width"]


def test_photo_altitude(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.altitude == photo["altitude"]


def test_photo_location(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        lat, lon = photo_obj.location
        assert (lat, lon) == photo["location"]
        photo_obj.location = (34.0, -118.0)
        assert photo_obj.location == (34.0, -118.0)
        photo_obj.location = (None, None)
        assert photo_obj.location == (None, None)


def test_photo_location_exception(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        with pytest.raises(ValueError):
            photo_obj.location = -90.0
        with pytest.raises(ValueError):
            photo_obj.location = (-91.0, 0.0)
        with pytest.raises(ValueError):
            photo_obj.location = (0.0, 181.0)


def test_photo_date(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        date = datetime.datetime.fromisoformat(photo["date"])
        local_tz = get_local_tz(datetime_remove_tz(date))
        date = datetime_remove_tz(date.astimezone(tz=local_tz))
        assert photo_obj.date == date


def test_photo_date_setter(photoslib: photoscript.PhotosLibrary):
    photo = PHOTOS_DICT[0]
    photo_obj = photoscript.Photo(photo["uuid"])
    photo_obj.date = datetime.datetime(2020, 9, 14, 1, 2, 3)
    assert photo_obj.date == datetime.datetime(2020, 9, 14, 1, 2, 3)


def test_photo_filename(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert photo_obj.filename == photo["filename"]


def test_photo_albums(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        assert sorted([album.name for album in photo_obj.albums]) == sorted(
            photo["albums"]
        )


def test_photo_export_basic(photoslib: photoscript.PhotosLibrary):
    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTOS_DICT[0]["uuid"])

    exported = photo.export(tmpdir.name)
    exported = [pathlib.Path(filename).name for filename in exported]
    expected = [f"{pathlib.Path(PHOTOS_DICT[0]['filename']).stem}.jpeg"]
    assert exported == expected
    files = os.listdir(tmpdir.name)
    assert files == expected


def test_export_photo_original_duplicate_overwrite(
    photoslib: photoscript.PhotosLibrary,
):
    """Test calling export twice resulting in
    duplicate filenames but use overwrite = true"""
    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTOS_DICT[0]["uuid"])
    exported1 = photo.export(tmpdir.name, original=True)
    exported2 = photo.export(tmpdir.name, original=True, overwrite=True)
    exported = list({pathlib.Path(filename).name for filename in exported1 + exported2})

    expected = [f"{pathlib.Path(PHOTOS_DICT[0]['filename']).stem}.jpeg"]

    # different versions of Photos may export the same photo as a different extension (.JPG vs .jpeg)
    # so compare only the stems
    assert stemset(exported) == stemset(expected)
    files = os.listdir(tmpdir.name)
    assert stemset(files) == stemset(expected)


def test_photo_duplicate(photoslib: photoscript.PhotosLibrary):
    for photo in PHOTOS_DICT:
        photo_obj = photoscript.Photo(photo["uuid"])
        new_photo = photo_obj.duplicate()
        assert isinstance(new_photo, photoscript.Photo)
        assert new_photo.filename == photo_obj.filename
