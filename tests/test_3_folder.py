""" Test Folder class """

import pytest
from applescript import AppleScript

import photoscript
from tests.conftest import get_os_version, photoslib, suspend_capture
from tests.photoscript_config_catalina import ALBUM_1_NAME, FOLDER_1_SUBFOLDERS

OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import (
        FOLDER_1_IDSTRING,
        FOLDER_1_LEN,
        FOLDER_1_NAME,
        FOLDER_1_SUBFOLDERS,
        FOLDER_1_UUID,
        FOLDER_1_UUID_OSXPHOTOS,
        FOLDER_2_LEN,
        FOLDER_2_NAME,
        FOLDER_2_PATH,
        FOLDER_2_PATH_STR,
        FOLDER_2_PATH_STR_COLON,
        FOLDER_2_UUID,
        FOLDER_3_ALBUMS,
        FOLDER_3_LEN,
        FOLDER_3_NAME,
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


def test_folder_init_uuid():
    """Test init with UUID"""
    folder = photoscript.Folder(FOLDER_1_UUID)
    assert isinstance(folder, photoscript.Folder)


def test_folder_init_osxphotos_uuid():
    """test Folder() with osxphotos style UUID"""
    folder = photoscript.Folder(FOLDER_1_UUID_OSXPHOTOS)
    assert isinstance(folder, photoscript.Folder)
    assert folder.id == FOLDER_1_UUID
    assert folder.uuid == FOLDER_1_UUID_OSXPHOTOS


def test_folder_init_path():
    """Test init with path"""
    folder = photoscript.Folder(path=[FOLDER_1_NAME])
    assert isinstance(folder, photoscript.Folder)
    assert folder.id == FOLDER_1_UUID


def test_folder_init_idstring():
    """Test init with idstring"""
    folder = photoscript.Folder(idstring=FOLDER_1_IDSTRING)
    assert isinstance(folder, photoscript.Folder)
    assert folder.id == FOLDER_1_UUID


def test_folder_init_too_many_1():
    """Test init with too many args"""
    with pytest.raises(ValueError):
        assert photoscript.Folder(uuid=FOLDER_1_UUID, idstring=FOLDER_1_IDSTRING)


def test_folder_init_too_many_2():
    """Test init with too many args"""
    with pytest.raises(ValueError):
        assert photoscript.Folder(path=[FOLDER_1_NAME], idstring=FOLDER_1_IDSTRING)


def test_folder_init_bad_uuid():
    """Test init with bad UUID"""
    with pytest.raises(ValueError):
        assert photoscript.Folder("BAD_UUID")


def test_folder_init_bad_path():
    """Test init with bad path"""
    with pytest.raises(ValueError):
        assert photoscript.Folder(path="BAD_PATH")


def test_folder_init_bad_idstring():
    """Test init with bad idstring"""
    with pytest.raises(ValueError):
        assert photoscript.Folder(idstring="BAD_IDSTRING")


def test_folder_id():
    """Test folder id"""
    folder = photoscript.Folder(FOLDER_1_UUID)
    assert folder.id == FOLDER_1_UUID


def test_folder_uuid():
    """Test folder uuid"""
    folder = photoscript.Folder(FOLDER_1_UUID)
    assert folder.uuid == FOLDER_1_UUID_OSXPHOTOS


def test_folder_name_title(photoslib):
    """Test folder name/title"""
    folder = photoslib.folder(FOLDER_1_NAME)
    assert folder.name == FOLDER_1_NAME
    assert folder.title == FOLDER_1_NAME


def test_folder_name_setter(photoslib):
    """ "Test setter for name"""
    folder = photoslib.folder(FOLDER_1_NAME)
    new_name = "My New Folder Name"
    folder.name = new_name
    assert folder.name == new_name
    assert folder.title == new_name


def test_folder_title_setter(photoslib):
    """Test setter for title"""
    folder = photoslib.folder(FOLDER_1_NAME)
    new_name = "My New Folder Name"
    folder.title = new_name
    assert folder.name == new_name
    assert folder.title == new_name


def test_folder_parent_id(photoslib):
    """ "Test parent_id top_level folder"""
    folder = photoslib.folder(FOLDER_1_NAME)
    assert folder.parent_id is None


def test_folder_parent_id_not_toplevel(photoslib):
    """Test parent id with non-top-level folder"""
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    assert folder.parent_id == FOLDER_1_IDSTRING


def test_folder_parent(photoslib):
    """Test folder parent"""
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    parent = folder.parent
    assert isinstance(parent, photoscript.Folder)
    assert parent.name == FOLDER_1_NAME


def test_folder_parent_top_level(photoslib):
    """Test folder parent with top-level folder"""
    folder = photoslib.folder(name=FOLDER_NAMES_TOP[0])
    assert folder.parent is None


def test_folder_path_str(photoslib):
    """Test folder path_str"""
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    assert folder.path_str() == FOLDER_2_PATH_STR
    assert folder.path_str(":") == FOLDER_2_PATH_STR_COLON
    with pytest.raises(ValueError):
        assert folder.path_str("FOO")


def test_folder_path(photoslib):
    """Test folder path"""
    folder = photoslib.folder(name=FOLDER_2_NAME, top_level=False)
    path = folder.path()
    assert len(path) == len(FOLDER_2_PATH)
    for i, p in enumerate(path):
        assert isinstance(p, photoscript.Folder)
        assert p.name == FOLDER_2_PATH[i]


def test_folder_albums(photoslib):
    """Test folder albums"""
    folder = photoslib.folder(FOLDER_3_NAME)
    albums = folder.albums
    assert sorted(album.name for album in albums) == sorted(FOLDER_3_ALBUMS)


def test_folder_album(photoslib):
    """Test folder album"""
    folder = photoslib.folder(FOLDER_3_NAME)
    album = folder.album(ALBUM_1_NAME)
    assert album.name == ALBUM_1_NAME


def test_folder_album_bad_name(photoslib):
    """Test folder album with bad name"""
    folder = photoslib.folder(FOLDER_3_NAME)
    album = folder.album("FOOBAR")
    assert album is None


def test_folder_subfolders(photoslib):
    """Test folder subfolders"""
    folder = photoslib.folder(FOLDER_1_NAME)
    subfolders = folder.subfolders
    assert sorted(f.name for f in subfolders) == sorted(FOLDER_1_SUBFOLDERS)


def test_folder_subfolders_none(photoslib):
    """Test folder subfolders with no subfolders"""
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    subfolders = folder.subfolders
    assert subfolders == []


def test_folder_folder(photoslib):
    """Test folder folder"""
    folder = photoslib.folder(FOLDER_1_NAME)
    subfolder = folder.folder(FOLDER_2_NAME)
    assert subfolder.name == FOLDER_2_NAME


def test_folder_folder_none(photoslib):
    """Test folder folder with no subfolder"""
    folder = photoslib.folder(FOLDER_1_NAME)
    subfolder = folder.folder("FOOBAR")
    assert subfolder is None


def test_folder_create_album(photoslib):
    """Test folder create_album"""
    folder = photoslib.folder(FOLDER_1_NAME)
    album = folder.create_album("New Album")
    assert isinstance(album, photoscript.Album)
    assert album.name == "New Album"
    assert album.parent.id == folder.id


def test_folder_create_folder(photoslib):
    """Test folder create_folder"""
    folder = photoslib.folder(FOLDER_1_NAME)
    subfolder = folder.create_folder("New Folder")
    assert isinstance(subfolder, photoscript.Folder)
    assert subfolder.name == "New Folder"
    assert subfolder.parent.id == folder.id


def test_len_1(photoslib):
    """test Folder.__len__"""
    folder = photoslib.folder(FOLDER_1_NAME)
    assert len(folder) == FOLDER_1_LEN


def test_len_2(photoslib):
    """test Folder.__len__"""
    folder = photoslib.folder(FOLDER_2_NAME, top_level=False)
    assert len(folder) == FOLDER_2_LEN


def test_len_3(photoslib):
    """test Folder.__len__"""
    folder = photoslib.folder(FOLDER_3_NAME)
    assert len(folder) == FOLDER_3_LEN
