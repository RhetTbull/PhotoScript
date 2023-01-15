""" Test Album class """

import os
import pathlib
import tempfile

import pytest
from applescript import AppleScript

import photoscript
from tests.conftest import get_os_version, photoslib, suspend_capture
from tests.photoscript_config_data import (
    ALBUM_1_NAME,
    ALBUM_1_PATH_STR,
    ALBUM_1_PATH_STR_COLON,
    ALBUM_1_PHOTO_EXPORT_FILENAMES,
    ALBUM_1_PHOTO_UUIDS,
    ALBUM_1_POST_REMOVE_UUIDS,
    ALBUM_1_REMOVE_UUIDS,
    ALBUM_1_UUID,
    ALBUM_1_UUID_OSXPHOTOS,
    ALBUM_NAMES_ALL,
    ALBUM_NAMES_TOP,
    EMPTY_ALBUM_NAME,
    FOLDER_NAME,
    FOLDER_NAMES_ALL,
    FOLDER_NAMES_TOP,
    FOLDER_UUID,
    IMPORT_PATHS,
    IMPORT_PHOTOS,
    NUM_PHOTOS,
    PHOTO_ADD_UUID,
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
from tests.utils import stemset

EMPTY_ALBUM_LEN = 0

########## Interactive tests run first ##########


########## Non-interactive tests ##########


def test_album_init():

    album = photoscript.Album(ALBUM_1_UUID)
    assert isinstance(album, photoscript.Album)


def test_album_init_osxphotos_uuid():
    """test Album() with osxphotos style UUID"""

    album = photoscript.Album(ALBUM_1_UUID_OSXPHOTOS)
    assert isinstance(album, photoscript.Album)
    assert album.id == ALBUM_1_UUID
    assert album.uuid == ALBUM_1_UUID_OSXPHOTOS


def test_album_init_bad_uuid():

    with pytest.raises(ValueError):
        assert photoscript.Album("BAD_UUID")


def test_album_id():

    album = photoscript.Album(ALBUM_1_UUID)
    assert album.id == ALBUM_1_UUID


def test_album_uuid():

    album = photoscript.Album(ALBUM_1_UUID)
    assert album.uuid == ALBUM_1_UUID_OSXPHOTOS


def test_len(photoslib: photoscript.PhotosLibrary):
    """test Album.__len__"""
    album = photoslib.album(ALBUM_1_NAME)
    assert len(album) == len(ALBUM_1_PHOTO_UUIDS)


def test_album_name_title(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(ALBUM_1_NAME)
    assert album.name == ALBUM_1_NAME
    assert album.title == ALBUM_1_NAME


def test_album_name_setter(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(ALBUM_1_NAME)
    new_name = "My New Album Name"
    album.name = new_name
    assert album.name == new_name
    assert album.title == new_name

    # reset name
    album.name = ALBUM_1_NAME


def test_album_title_setter(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(ALBUM_1_NAME)
    new_name = "My New Album Name"
    album.title = new_name
    assert album.name == new_name
    assert album.title == new_name

    # reset title
    album.title = ALBUM_1_NAME


def test_album_parent_id(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(ALBUM_1_NAME)
    assert album.parent.id == FOLDER_UUID


def test_album_parent(photoslib: photoscript.PhotosLibrary):

    album = photoslib.album(ALBUM_1_NAME)
    parent = album.parent
    assert isinstance(parent, photoscript.Folder)
    assert parent.name == FOLDER_NAME


def test_album_parent_top_level(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(ALBUM_NAMES_TOP[0])
    assert album.parent is None


def test_album_path_str(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(ALBUM_1_NAME)
    assert album.path_str() == ALBUM_1_PATH_STR
    assert album.path_str(":") == ALBUM_1_PATH_STR_COLON
    with pytest.raises(ValueError):
        assert album.path_str("FOO")


def test_album_photos(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(ALBUM_1_NAME)
    photo_ids = [p.id for p in album.photos()]
    assert sorted(photo_ids) == sorted(ALBUM_1_PHOTO_UUIDS)


def test_album_photos_empty(photoslib: photoscript.PhotosLibrary):
    album = photoslib.album(EMPTY_ALBUM_NAME)
    assert album.photos() == []


def test_album_photos_add(photoslib: photoscript.PhotosLibrary):

    global EMPTY_ALBUM_LEN
    album = photoslib.album(EMPTY_ALBUM_NAME)
    assert len(album) == 0
    added = album.add([photoscript.Photo(PHOTO_ADD_UUID)])
    assert len(album) == 1
    assert len(added) == 1
    assert added[0].id == PHOTO_ADD_UUID
    assert album.photos()[0].id == PHOTO_ADD_UUID

    EMPTY_ALBUM_LEN = len(album)


def test_album_photos_add_none(photoslib: photoscript.PhotosLibrary):
    """Test add with no photos"""

    album = photoslib.album(ALBUM_1_NAME)
    album_length = len(album)
    album.add([])
    assert len(album) == album_length


def test_album_import_photos(photoslib: photoscript.PhotosLibrary):
    """Test import photo"""

    global EMPTY_ALBUM_LEN
    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    album = photoslib.album(EMPTY_ALBUM_NAME)
    imported = album.import_photos(photo_paths)
    assert len(imported) == len(IMPORT_PATHS)
    assert len(album) == EMPTY_ALBUM_LEN + len(IMPORT_PATHS)

    EMPTY_ALBUM_LEN = len(album)


def test_album_import_photos_skip_dup_check(photoslib: photoscript.PhotosLibrary):
    """Attempt to import a duplicate photo with skip_duplicate_check = True
    This will cause a duplicate photo to be imported"""

    # this test must be run after the previous test
    global EMPTY_ALBUM_LEN

    album = photoslib.album(EMPTY_ALBUM_NAME)
    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    imported = album.import_photos(photo_paths, skip_duplicate_check=True)
    assert len(imported) == len(IMPORT_PATHS)
    assert len(album) == EMPTY_ALBUM_LEN + len(IMPORT_PATHS)

    EMPTY_ALBUM_LEN = len(album)


def test_album_export_photos_basic(photoslib: photoscript.PhotosLibrary):

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")
    album = photoslib.album(ALBUM_1_NAME)
    exported = album.export(tmpdir.name)
    exported = [pathlib.Path(filename).name for filename in exported]
    assert sorted(exported) == ALBUM_1_PHOTO_EXPORT_FILENAMES
    files = os.listdir(tmpdir.name)
    assert sorted(files) == sorted(ALBUM_1_PHOTO_EXPORT_FILENAMES)


def test_album_export_photos_duplicate_overwrite(photoslib: photoscript.PhotosLibrary):
    """Test calling export twice resulting in
    duplicate filenames but use overwrite = true"""

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")
    album = photoslib.album(ALBUM_1_NAME)
    exported1 = album.export(tmpdir.name, overwrite=True, original=True)
    exported2 = album.export(tmpdir.name, overwrite=True, original=True)
    exported = list({pathlib.Path(filename).name for filename in exported1 + exported2})

    # some versions of macOS use .JPG and some use .jpeg
    assert stemset(exported) == stemset(ALBUM_1_PHOTO_EXPORT_FILENAMES)
    files = os.listdir(tmpdir.name)
    assert stemset(files) == stemset(ALBUM_1_PHOTO_EXPORT_FILENAMES)


def test_album_remove_by_id(photoslib: photoscript.PhotosLibrary):
    """Test album.remove_by_id"""

    album = photoslib.album(ALBUM_1_NAME)
    parent_id = album.parent.id
    new_album = album.remove_by_id(ALBUM_1_REMOVE_UUIDS)
    assert isinstance(new_album, photoscript.Album)
    uuids = [photo.id for photo in new_album.photos()]
    assert sorted(uuids) == sorted(ALBUM_1_POST_REMOVE_UUIDS)
    assert new_album.title == ALBUM_1_NAME
    assert new_album.parent.id == parent_id
    assert album.id == new_album.id
    assert album.uuid == new_album.uuid


def test_album_remove(photoslib: photoscript.PhotosLibrary):
    """Test album.remove"""

    album = photoslib.album(ALBUM_1_NAME)
    photos = [photoscript.Photo(uuid) for uuid in ALBUM_1_REMOVE_UUIDS]
    new_album = album.remove(photos)
    assert isinstance(new_album, photoscript.Album)
    uuids = [photo.id for photo in new_album.photos()]
    assert sorted(uuids) == sorted(ALBUM_1_POST_REMOVE_UUIDS)
    assert new_album.title == ALBUM_1_NAME
    assert new_album.id == album.id
