""" Test Folder class """

import pytest
from applescript import AppleScript
from tests.conftest import photoslib, suspend_capture, get_os_version


OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import (
        FOLDER_NAMES_ALL,
        FOLDER_NAMES_TOP,
        FOLDER_1_LEN,
        FOLDER_1_NAME,
        FOLDER_1_UUID,
        FOLDER_1_UUID_OSXPHOTOS,
        FOLDER_2_LEN,
        FOLDER_2_NAME,
        FOLDER_2_UUID,
        FOLDER_2_PATH,
        FOLDER_2_PATH_STR,
        FOLDER_2_PATH_STR_COLON,
        FOLDER_3_LEN,
        FOLDER_3_NAME,
        FOLDER_3_ALBUMS,
        FOLDER_3_UUID,
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


def test_folder_init():
    import photoscript

    folder = photoscript.Folder(FOLDER_1_UUID)
    assert isinstance(folder, photoscript.Folder)


def test_folder_init_osxphotos_uuid():
    """ test Folder() with osxphotos style UUID """
    import photoscript

    folder = photoscript.Folder(FOLDER_1_UUID_OSXPHOTOS)
    assert isinstance(folder, photoscript.Folder)
    assert folder.id == FOLDER_1_UUID
    assert folder.uuid == FOLDER_1_UUID_OSXPHOTOS


def test_folder_init_bad_uuid():
    import photoscript

    with pytest.raises(ValueError):
        assert photoscript.Folder("BAD_UUID")


def test_folder_id():
    import photoscript

    folder = photoscript.Folder(FOLDER_1_UUID)
    assert folder.id == FOLDER_1_UUID


def test_folder_uuid():
    import photoscript

    folder = photoscript.Folder(FOLDER_1_UUID)
    assert folder.uuid == FOLDER_1_UUID_OSXPHOTOS


def test_folder_name_title(photoslib):
    folder = photoslib.folder(FOLDER_1_NAME)
    assert folder.name == FOLDER_1_NAME
    assert folder.title == FOLDER_1_NAME


def test_folder_name_setter(photoslib):
    folder = photoslib.folder(FOLDER_1_NAME)
    new_name = "My New Folder Name"
    folder.name = new_name
    assert folder.name == new_name
    assert folder.title == new_name


def test_folder_title_setter(photoslib):
    folder = photoslib.folder(FOLDER_1_NAME)
    new_name = "My New Folder Name"
    folder.title = new_name
    assert folder.name == new_name
    assert folder.title == new_name


def test_folder_parent_id(photoslib):
    folder = photoslib.folder(FOLDER_1_NAME)
    assert folder.parent_id is None


def test_folder_parent_id(photoslib):
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    assert folder.parent_id == FOLDER_1_UUID


def test_folder_parent(photoslib):
    import photoscript

    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    parent = folder.parent
    assert isinstance(parent, photoscript.Folder)
    assert parent.name == FOLDER_1_NAME


def test_folder_parent_top_level(photoslib):
    folder = photoslib.folder(FOLDER_NAMES_TOP[0])
    assert folder.parent is None


def test_folder_path_str(photoslib):
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    assert folder.path_str() == FOLDER_2_PATH_STR
    assert folder.path_str(":") == FOLDER_2_PATH_STR_COLON
    with pytest.raises(ValueError):
        assert folder.path_str("FOO")


def test_folder_path(photoslib):
    import photoscript

    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    path = folder.path()
    assert len(path) == len(FOLDER_2_PATH)
    for i, p in enumerate(path):
        assert isinstance(p, photoscript.Folder)
        assert p.name == FOLDER_2_PATH[i]

def test_folder_albums(photoslib):
    folder = photoslib.folder(FOLDER_3_NAME)
    albums = folder.albums
    assert sorted(album.name for album in albums) == sorted(FOLDER_3_ALBUMS)

def test_len_1(photoslib):
    """ test Album.__len__ """
    folder = photoslib.folder(FOLDER_1_NAME)
    assert len(folder) == FOLDER_1_LEN


def test_len_2(photoslib):
    """ test Album.__len__ """
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    assert len(folder) == FOLDER_2_LEN


def test_len_3(photoslib):
    """ test Album.__len__ """
    folder = photoslib.folder(FOLDER_3_NAME)
    assert len(folder) == FOLDER_3_LEN
