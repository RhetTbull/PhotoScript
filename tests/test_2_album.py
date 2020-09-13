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
        ALBUM_1_PATH_STR,
        ALBUM_1_PATH_STR_COLON,
        ALBUM_1_PHOTO_UUIDS,
        ALBUM_1_PHOTO_EXPORT_FILENAMES,
        ALBUM_1_REMOVE_UUIDS,
        ALBUM_1_POST_REMOVE_UUIDS,
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
else:
    pytest.exit("This test suite currently only runs on MacOS Catalina ")

########## Interactive tests run first ##########


########## Non-interactive tests ##########


def test_album_init():
    import photoscript

    album = photoscript.Album(ALBUM_1_UUID)
    assert isinstance(album, photoscript.Album)


def test_album_init_osxphotos_uuid():
    """ test Album() with osxphotos style UUID """
    import photoscript

    album = photoscript.Album(ALBUM_1_UUID_OSXPHOTOS)
    assert isinstance(album, photoscript.Album)
    assert album.id == ALBUM_1_UUID
    assert album.uuid == ALBUM_1_UUID_OSXPHOTOS


def test_album_init_bad_uuid():
    import photoscript

    with pytest.raises(ValueError):
        assert photoscript.Album("BAD_UUID")


def test_album_id():
    import photoscript

    album = photoscript.Album(ALBUM_1_UUID)
    assert album.id == ALBUM_1_UUID


def test_album_uuid():
    import photoscript

    album = photoscript.Album(ALBUM_1_UUID)
    assert album.uuid == ALBUM_1_UUID_OSXPHOTOS


def test_album_name_title(photoslib):
    album = photoslib.album(ALBUM_1_NAME)
    assert album.name == ALBUM_1_NAME
    assert album.title == ALBUM_1_NAME


def test_album_name_setter(photoslib):
    album = photoslib.album(ALBUM_1_NAME)
    new_name = "My New Album Name"
    album.name = new_name
    assert album.name == new_name
    assert album.title == new_name


def test_album_title_setter(photoslib):
    album = photoslib.album(ALBUM_1_NAME)
    new_name = "My New Album Name"
    album.title = new_name
    assert album.name == new_name
    assert album.title == new_name


def test_album_parent_id(photoslib):
    album = photoslib.album(ALBUM_1_NAME)
    assert album.parent_id == FOLDER_UUID


def test_album_parent(photoslib):
    import photoscript

    album = photoslib.album(ALBUM_1_NAME)
    parent = album.parent
    assert isinstance(parent, photoscript.Folder)
    assert parent.name == FOLDER_NAME


def test_album_parent_top_level(photoslib):
    album = photoslib.album(ALBUM_NAMES_TOP[0])
    assert album.parent is None


def test_album_path_str(photoslib):
    album = photoslib.album(ALBUM_1_NAME)
    assert album.path_str() == ALBUM_1_PATH_STR
    assert album.path_str(":") == ALBUM_1_PATH_STR_COLON
    with pytest.raises(ValueError):
        assert album.path_str("FOO")


def test_album_photos(photoslib):
    album = photoslib.album(ALBUM_1_NAME)
    photo_ids = [p.id for p in album.photos()]
    assert sorted(photo_ids) == sorted(ALBUM_1_PHOTO_UUIDS)


def test_album_photos_empty(photoslib):
    album = photoslib.album(EMPTY_ALBUM_NAME)
    assert album.photos() == []


def test_album_photos_add(photoslib):
    import photoscript

    album = photoslib.album(EMPTY_ALBUM_NAME)
    assert len(album) == 0
    added = album.add([photoscript.Photo(PHOTO_ADD_UUID)])
    assert len(album) == 1
    assert len(added) == 1
    assert added[0].id == PHOTO_ADD_UUID
    assert album.photos()[0].id == PHOTO_ADD_UUID


def test_album_photos_add_none(photoslib):
    """ Test add with no photos """
    import photoscript

    album = photoslib.album(ALBUM_1_NAME)
    album_length = len(album)
    album.add([])
    assert len(album) == album_length


def test_album_import_photos(photoslib):
    """ Test import photo """
    import os
    import pathlib

    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    album = photoslib.album(EMPTY_ALBUM_NAME)
    imported = album.import_photos(photo_paths)
    assert len(imported) == len(IMPORT_PATHS)
    assert len(album) == len(IMPORT_PATHS)


def test_album_import_photos_skip_dup_check(photoslib):
    """ Attempt to import a duplicate photo with skip_duplicate_check = True
        This will cause a duplicate photo to be imported """
    import os
    import pathlib

    album = photoslib.album(EMPTY_ALBUM_NAME)
    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    imported = album.import_photos(photo_paths)
    imported = album.import_photos(photo_paths, skip_duplicate_check=True)
    assert len(imported) == len(IMPORT_PATHS)
    assert len(album) == 2 * len(IMPORT_PATHS)


def test_album_export_photos_basic(photoslib):
    import os
    import pathlib
    import tempfile

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")
    album = photoslib.album(ALBUM_1_NAME)
    exported = album.export(tmpdir.name)
    exported = [pathlib.Path(filename).name for filename in exported]
    assert sorted(exported) == ALBUM_1_PHOTO_EXPORT_FILENAMES
    files = os.listdir(tmpdir.name)
    assert sorted(files) == sorted(ALBUM_1_PHOTO_EXPORT_FILENAMES)


def test_album_export_photos_duplicate_overwrite(photoslib):
    """ Test calling export twice resulting in 
        duplicate filenames but use overwrite = true"""
    import os
    import pathlib
    import tempfile

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")
    album = photoslib.album(ALBUM_1_NAME)
    exported1 = album.export(tmpdir.name, overwrite=True, original=True)
    exported2 = album.export(tmpdir.name, overwrite=True, original=True)
    exported = list({pathlib.Path(filename).name for filename in exported1 + exported2})

    assert sorted(exported) == ALBUM_1_PHOTO_EXPORT_FILENAMES
    files = os.listdir(tmpdir.name)
    assert sorted(files) == sorted(ALBUM_1_PHOTO_EXPORT_FILENAMES)


def test_album_remove_by_id(photoslib):
    """ Test album.remove_by_id """
    import photoscript

    album = photoslib.album(ALBUM_1_NAME)
    parent_id = album.parent.id
    new_album = album.remove_by_id(ALBUM_1_REMOVE_UUIDS)
    assert isinstance(new_album, photoscript.Album)
    uuids = [photo.id for photo in new_album.photos()]
    assert sorted(uuids) == sorted(ALBUM_1_POST_REMOVE_UUIDS)
    assert new_album.title == ALBUM_1_NAME
    assert new_album.id == album.id
    assert new_album.parent.id == parent_id


def test_album_remove(photoslib):
    """ Test album.remove """
    import photoscript

    album = photoslib.album(ALBUM_1_NAME)
    photos = [photoscript.Photo(uuid) for uuid in ALBUM_1_REMOVE_UUIDS]
    new_album = album.remove(photos)
    assert isinstance(new_album, photoscript.Album)
    uuids = [photo.id for photo in new_album.photos()]
    assert sorted(uuids) == sorted(ALBUM_1_POST_REMOVE_UUIDS)
    assert new_album.title == ALBUM_1_NAME
    assert new_album.id == album.id


def test_len(photoslib):
    """ test Album.__len__ """
    album = photoslib.album(ALBUM_1_NAME)
    assert len(album) == len(ALBUM_1_PHOTO_UUIDS)
