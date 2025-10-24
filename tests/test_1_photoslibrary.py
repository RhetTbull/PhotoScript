""" Test PhotosLibrary class """

import os
import pathlib
import tempfile
import time

import pytest
from applescript import AppleScript
from flaky import flaky

import photoscript
from photoscript.utils import get_os_version
from tests.conftest import photoslib, suspend_capture
from tests.photoscript_config_catalina import PHOTO_EXPORT_FILENAME_ORIGINAL
from tests.photoscript_config_data import (
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
    PHOTO_EXPORT_2_FILENAMES,
    PHOTO_EXPORT_2_FILENAMES_ORIGINAL,
    PHOTO_EXPORT_FILENAME,
    PHOTO_EXPORT_UUID,
    PHOTO_FAVORITES_SET_UUID,
    PHOTO_FAVORITES_UNSET_UUID,
    PHOTOS_FAVORITES,
    PHOTOS_FAVORITES_SET,
    PHOTOS_FILENAMES,
    PHOTOS_PLANTS,
    PHOTOS_UUID,
    PHOTOS_UUID_FILENAMES,
    SELECTION_UUIDS,
    TEST_LIBRARY,
    TEST_LIBRARY_OPEN,
)
from tests.utils import stemset


def test_photoslibrary_activate(photoslib: photoscript.PhotosLibrary):

    photoslib.activate()
    assert photoslib.frontmost


@pytest.mark.skip(reason="run test isolated works, but not after test_photoslibrary_quit. Photos shows up as active but not visible.")
def test_photoslibrary_quit(photoslib: photoscript.PhotosLibrary):

    photoslib.quit()
    script = AppleScript(
        """
            on is_running(appName)
                tell application "System Events" to (name of processes) contains appName
            end is_running
        """
    )
    assert not script.call("is_running", "Photos")

@pytest.mark.skip(reason="run test isolated works, but not after test_photoslibrary_quit. Photos shows up as active but not visible.")
def test_photoslibrary_running(photoslib: photoscript.PhotosLibrary):

    assert photoslib.running
    photoslib.quit()
    time.sleep(3)  # give photos time to quit
    assert not photoslib.running


@pytest.mark.skip(reason="test does not work on Ventura even though Photos is hidden")
@flaky(max_runs=3, min_passes=1)
def test_photoslibrary_hide(photoslib: photoscript.PhotosLibrary):
    """Test hide()"""

    # due to pytest weirdness, need to create a new photoslib object
    # to get hide and hidden to work as they would in a real script
    # on Ventura, this test fails even though Photos is hidden correctly s
    photoslib.quit()
    photoslib = photoscript.PhotosLibrary()
    photoslib.activate()
    time.sleep(1)
    photoslib.hide()
    time.sleep(1)
    assert not photoslib.frontmost
    assert photoslib.hidden


@pytest.mark.skip(reason="test does not work on Ventura even though Photos is hidden")
@flaky(max_runs=3, min_passes=1)
def test_photoslibrary_hidden(photoslib: photoscript.PhotosLibrary):
    """Test hidden"""

    # due to pytest weirdness, need to create a new photoslib object
    # to get hide and hidden to work as they would in a real script
    # on Ventura, this test fails even though Photos is hidden correctly s
    photoslib.quit()
    photoslib = photoscript.PhotosLibrary()
    photoslib.activate()
    time.sleep(1)
    assert not photoslib.hidden
    photoslib.hide()
    time.sleep(1)
    assert photoslib.hidden

@pytest.mark.skip(reason="run test isolated works, but not after test_photoslibrary_quit. Photos shows up as active but not visible.")
def test_photoslibrary_name(photoslib: photoscript.PhotosLibrary):
    assert photoslib.name == "Photos"


def test_photoslibrary_version(photoslib: photoscript.PhotosLibrary):
    photo_ver = photoslib.version
    assert photo_ver is not None


def test_photoslibrary_frontmost(photoslib: photoscript.PhotosLibrary):

    photoslib.activate()
    assert photoslib.frontmost

    script = AppleScript(
        """
            tell application "Finder" to activate
            delay 2
        """
    )
    photoslib.hide()
    script.run()
    assert not photoslib.frontmost


def test_photoslibrary_favorites(photoslib: photoscript.PhotosLibrary):

    favorites = photoslib.favorites
    fav_names = [photo.filename for photo in favorites.photos()]
    assert sorted(fav_names) == sorted(PHOTOS_FAVORITES)

    # set/unset favorites and check again
    photo = next(photoslib.photos(uuid=[PHOTO_FAVORITES_SET_UUID]))
    photo.favorite = True
    photo = next(photoslib.photos(uuid=[PHOTO_FAVORITES_UNSET_UUID]))
    photo.favorite = False

    favorites = photoslib.favorites
    fav_names = [photo.filename for photo in favorites.photos()]
    assert sorted(fav_names) == sorted(PHOTOS_FAVORITES_SET)


def test_photoslibrary_photos_no_args(photoslib: photoscript.PhotosLibrary):
    photos = photoslib.photos()
    filenames = [photo.filename for photo in photos]
    assert sorted(filenames) == sorted(PHOTOS_FILENAMES)


def test_photoslibrary_photos_search(photoslib: photoscript.PhotosLibrary):
    photos = photoslib.photos(search="plants")
    filenames = [photo.filename for photo in photos]
    assert sorted(filenames) == sorted(PHOTOS_PLANTS)


def test_photoslibrary_photos_search_no_results(photoslib: photoscript.PhotosLibrary):
    photos = photoslib.photos(search="fish")
    filenames = [photo.filename for photo in photos]
    assert not filenames


def test_photoslibrary_photos_uuid(photoslib: photoscript.PhotosLibrary):
    photos = photoslib.photos(uuid=PHOTOS_UUID)
    filenames = [photo.filename for photo in photos]
    assert sorted(filenames) == sorted(PHOTOS_UUID_FILENAMES)


def test_photoslibrary_photos_exception(photoslib: photoscript.PhotosLibrary):
    with pytest.raises(ValueError):
        photoslib.photos(uuid=PHOTOS_UUID, search="plants")


def test_photoslibrary_photos_range(photoslib: photoscript.PhotosLibrary):
    photos = photoslib.photos(range_=[0, NUM_PHOTOS])
    filenames = [photo.filename for photo in photos]
    assert sorted(filenames) == sorted(PHOTOS_FILENAMES)


def test_photoslibrary_photos_range_single(photoslib: photoscript.PhotosLibrary):
    photos = photoslib.photos(range_=[NUM_PHOTOS - 1])
    filenames = [photo.filename for photo in photos]
    assert len(filenames) == NUM_PHOTOS - 1


def test_photoslibrary_photos_range_exception(photoslib: photoscript.PhotosLibrary):
    with pytest.raises(ValueError):
        photoslib.photos(range_=[0, NUM_PHOTOS + 1])
    with pytest.raises(ValueError):
        photoslib.photos(range_=[NUM_PHOTOS, 0])
    with pytest.raises(TypeError):
        photoslib.photos(range_=1)
    with pytest.raises(ValueError):
        photoslib.photos(range_=[1, 2, 3])


def test_photoslibrary_import_photos(photoslib: photoscript.PhotosLibrary):

    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photos = photoslib.import_photos(photo_paths)
    assert isinstance(photos[0], photoscript.Photo)
    filenames = [photo.filename for photo in photos]
    assert filenames == IMPORT_PHOTOS


def test_photoslibrary_import_photos_skip_dup_check(
    photoslib: photoscript.PhotosLibrary,
):
    """Attempt to import a duplicate photo with skip_duplicate_check = True
    This will cause a duplicate photo to be imported"""

    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photoslib.import_photos(photo_paths, skip_duplicate_check=True)
    photos = list(photoslib.photos())
    assert len(photos) == NUM_PHOTOS + 2


def test_photoslibrary_create_album(photoslib: photoscript.PhotosLibrary):

    global ALBUM_NAMES_ALL, ALBUM_NAMES_TOP

    album = photoslib.create_album("New Album")
    assert isinstance(album, photoscript.Album)

    albums = photoslib.album_names()
    assert "New Album" in albums

    # set up for future tests
    ALBUM_NAMES_ALL.append("New Album")
    ALBUM_NAMES_TOP.append("New Album")


def test_photoslibrary_import_photos_album(photoslib: photoscript.PhotosLibrary):

    album = photoslib.album("New Album")
    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photoslib.import_photos(photo_paths, album=album, skip_duplicate_check=True)
    photos = album.photos()
    filenames = [photo.filename for photo in photos]
    for filename in IMPORT_PHOTOS:
        assert filename in filenames


def test_photoslibrary_album_names(photoslib: photoscript.PhotosLibrary):

    albums = photoslib.album_names()
    assert sorted(albums) == sorted(ALBUM_NAMES_ALL)


def test_photoslibrary_album_names_top(photoslib: photoscript.PhotosLibrary):

    albums = photoslib.album_names(top_level=True)
    assert sorted(albums) == sorted(ALBUM_NAMES_TOP)


def test_photoslibrary_folder_names(photoslib: photoscript.PhotosLibrary):

    folders = photoslib.folder_names()
    assert sorted(folders) == sorted(FOLDER_NAMES_ALL)


def test_photoslibrary_folder_names_top(photoslib: photoscript.PhotosLibrary):

    folders = photoslib.folder_names(top_level=True)
    assert sorted(folders) == sorted(FOLDER_NAMES_TOP)


def test_photoslibrary_album_by_name(photoslib: photoscript.PhotosLibrary):

    album = photoslib.album(ALBUM_1_NAME)
    assert album is not None
    assert isinstance(album, photoscript.Album)


def test_photoslibrary_album_by_uuid(photoslib: photoscript.PhotosLibrary):

    album = photoslib.album(uuid=ALBUM_1_UUID)
    assert album is not None
    assert isinstance(album, photoscript.Album)


def test_photoslibrary_album_bad_name(photoslib: photoscript.PhotosLibrary):

    album = photoslib.album("BAD_NAME")
    assert album is None


def test_photoslibrary_album_bad_uuid(photoslib: photoscript.PhotosLibrary):

    with pytest.raises(ValueError):
        photoslib.album(uuid="BAD_UUID")


def test_photoslibrary_album_exception_1(photoslib: photoscript.PhotosLibrary):
    with pytest.raises(ValueError):
        photoslib.album()


def test_photoslibrary_album_exception_2(photoslib: photoscript.PhotosLibrary):
    with pytest.raises(ValueError):
        photoslib.album(ALBUM_1_NAME, uuid=ALBUM_1_UUID)


def test_photoslibrary_albums(photoslib: photoscript.PhotosLibrary):
    albums = photoslib.albums()
    assert len(albums) == len(ALBUM_NAMES_ALL)
    album_names = [album.name for album in albums]
    assert sorted(album_names) == sorted(ALBUM_NAMES_ALL)


def test_photoslibrary_albums_top(photoslib: photoscript.PhotosLibrary):
    albums = photoslib.albums(top_level=True)
    assert len(albums) == len(ALBUM_NAMES_TOP)
    album_names = [album.name for album in albums]
    assert sorted(album_names) == sorted(ALBUM_NAMES_TOP)


def test_photoslibrary_create_album_error(photoslib: photoscript.PhotosLibrary):

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_album("New Album")
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_create_album_at_folder(photoslib: photoscript.PhotosLibrary):

    album = photoslib.create_album(
        "New Album In Folder", folder=photoslib.folder("Folder1", top_level=True)
    )
    assert isinstance(album, photoscript.Album)

    albums = photoslib.album_names()
    assert "New Album In Folder" in albums

    assert album.parent.name == "Folder1"


def test_photoslibrary_create_album_at_folder_error(
    photoslib: photoscript.PhotosLibrary,
):

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    folder = photoslib.folder("Folder1")
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_album("New Album", folder=folder)
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_delete_album(photoslib: photoscript.PhotosLibrary):

    album = photoslib.album("Farmers Market")
    photoslib.delete_album(album)
    assert "Farmers Market" not in photoslib.album_names()


def test_photoslibrary_folder(photoslib: photoscript.PhotosLibrary):

    folder = photoslib.folder("Folder1")
    assert isinstance(folder, photoscript.Folder)
    subfolders = folder.subfolders
    assert len(subfolders) == 1
    assert subfolders[0].name == "SubFolder1"


def test_photoslibrary_folder_top_level(photoslib: photoscript.PhotosLibrary):

    folder = photoslib.folder("SubFolder1", top_level=True)
    assert folder is None


def test_photoslibrary_folder_exception_1(photoslib: photoscript.PhotosLibrary):
    """test exceptions in folder()"""

    with pytest.raises(ValueError):
        folder = photoslib.folder()


def test_photoslibrary_folder_exception_2(photoslib: photoscript.PhotosLibrary):
    """test exceptions in folder()"""

    with pytest.raises(ValueError):
        folder = photoslib.folder("Travel", uuid=FOLDER_UUID)


def test_photoslibrary_folder_by_uuid(photoslib: photoscript.PhotosLibrary):
    """test getting folder by UUID"""

    folder = photoslib.folder(uuid=FOLDER_UUID)
    assert isinstance(folder, photoscript.Folder)
    assert folder.name == FOLDER_NAME


def test_photoslibrary_folder_bad_uuid(photoslib: photoscript.PhotosLibrary):
    """test getting folder by invalid UUID"""
    assert photoslib.folder(uuid="BAD_UUID") is None


def test_photoslibrary_folder_by_path_1(photoslib: photoscript.PhotosLibrary):

    folder = photoslib.folder_by_path(["Travel"])
    assert isinstance(folder, photoscript.Folder)


def test_photoslibrary_folder_by_path_2(photoslib: photoscript.PhotosLibrary):

    folder = photoslib.folder_by_path(["Folder1", "SubFolder1"])
    assert isinstance(folder, photoscript.Folder)


def test_photoslibrary_folder_by_path_bad_path(photoslib: photoscript.PhotosLibrary):

    folder = photoslib.folder_by_path(["Folder1", "SubFolder1", "I Don't Exist"])
    assert folder is None


def test_photoslibrary_folders_top_level(photoslib: photoscript.PhotosLibrary):
    folders = photoslib.folders()
    folder_names = [folder.name for folder in folders]
    assert sorted(folder_names) == sorted(FOLDER_NAMES_TOP)


def test_photoslibrary_folders_all(photoslib: photoscript.PhotosLibrary):
    folders = photoslib.folders(top_level=False)
    folder_names = [folder.name for folder in folders]
    assert sorted(folder_names) == sorted(FOLDER_NAMES_ALL)


def test_photoslibrary_create_folder(photoslib: photoscript.PhotosLibrary):

    global FOLDER_NAMES_TOP, FOLDER_NAMES_ALL

    folder = photoslib.create_folder("New Folder")
    assert isinstance(folder, photoscript.Folder)

    folders = photoslib.folder_names()
    assert "New Folder" in folders

    # set up for next test
    FOLDER_NAMES_TOP.append("New Folder")
    FOLDER_NAMES_ALL.append("New Folder")


def test_photoslibrary_create_folder_error(photoslib: photoscript.PhotosLibrary):

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_folder("New Folder")
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_create_folder_at_folder(photoslib: photoscript.PhotosLibrary):

    global FOLDER_NAMES_ALL

    folder = photoslib.create_folder("New SubFolder", folder=photoslib.folder("Travel"))
    assert isinstance(folder, photoscript.Folder)

    folders = photoslib.folder_names(top_level=True)
    assert "New SubFolder" not in folders

    folders = photoslib.folder_names()
    assert "New SubFolder" in folders

    assert folder.parent.name == "Travel"

    # set up for next test
    FOLDER_NAMES_ALL.append("New SubFolder")


def test_photoslibrary_create_folder_at_folder_error(
    photoslib: photoscript.PhotosLibrary,
):

    folder = photoslib.folder("Travel")

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_folder("New Folder", folder=folder)
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_make_folders_exist(photoslib: photoscript.PhotosLibrary):
    """test make_folders with path that exists"""

    subfolder = photoslib.folder("SubFolder1", top_level=False)
    folder = photoslib.make_folders(["Folder1", "SubFolder1"])
    assert isinstance(folder, photoscript.Folder)
    assert len(photoslib.folders(top_level=False)) == len(FOLDER_NAMES_ALL)
    assert subfolder.id == folder.id


def test_photoslibrary_make_folders_new(photoslib: photoscript.PhotosLibrary):
    """test make_folders with entirely new path"""

    global FOLDER_NAMES_ALL, FOLDER_NAMES_TOP

    folder = photoslib.make_folders(["Folder2", "SubFolder2"])
    assert isinstance(folder, photoscript.Folder)
    assert len(photoslib.folders(top_level=False)) == len(FOLDER_NAMES_ALL) + 2

    # set up for next test
    FOLDER_NAMES_ALL.extend(["Folder2", "SubFolder2"])
    FOLDER_NAMES_TOP.append("Folder2")


def test_photoslibrary_make_folders_new_exist(photoslib: photoscript.PhotosLibrary):
    """test make_folders with new path inside existing path"""

    global FOLDER_NAMES_ALL

    subfolder = photoslib.folder("SubFolder1", top_level=False)
    folder = photoslib.make_folders(["Folder1", "SubFolder1", "New Sub Folder"])
    assert isinstance(folder, photoscript.Folder)
    assert len(photoslib.folders(top_level=False)) == len(FOLDER_NAMES_ALL) + 1
    assert folder.parent.id == subfolder.id

    # set up for next test
    FOLDER_NAMES_ALL.append("New Sub Folder")


def test_photoslibrary_make_folders_bad_type(photoslib: photoscript.PhotosLibrary):
    """test make_folders with non-list value for folders"""
    with pytest.raises(TypeError):
        photoslib.make_folders("Folder1")


def test_photoslibrary_make_folders_bad_value(photoslib: photoscript.PhotosLibrary):
    """test make_folders with empty value for folders"""
    with pytest.raises(ValueError):
        photoslib.make_folders([])


def test_photoslibrary_make_album_folders_new_path(
    photoslib: photoscript.PhotosLibrary,
):
    """test make_album_folders with new path"""

    global ALBUM_NAMES_ALL, FOLDER_NAMES_ALL, FOLDER_NAMES_TOP

    album = photoslib.make_album_folders("New Album", ["Folder3", "SubFolder3"])
    assert isinstance(album, photoscript.Album)
    assert "New Album" in photoslib.album_names(top_level=False)

    # set up for next test
    ALBUM_NAMES_ALL.append("New Album")
    FOLDER_NAMES_ALL.extend(["Folder3", "SubFolder3"])
    FOLDER_NAMES_TOP.append("Folder3")


def test_photoslibrary_make_album_folders_new_album(
    photoslib: photoscript.PhotosLibrary,
):
    """test make_album_folders with new album in existing folder"""

    global ALBUM_NAMES_ALL

    album = photoslib.make_album_folders("New Album", ["Folder1", "SubFolder1"])
    assert isinstance(album, photoscript.Album)
    assert "New Album" in photoslib.album_names(top_level=False)

    # set up for next test
    ALBUM_NAMES_ALL.append("New Album")


def test_photoslibrary_make_album_folders_existing_album(
    photoslib: photoscript.PhotosLibrary,
):
    """test make_album_folders with new album in existing folder"""

    album = photoslib.album("San Juan Capistrano")
    new_album = photoslib.make_album_folders("San Juan Capistrano", ["Travel"])
    assert isinstance(album, photoscript.Album)
    assert album.id == new_album.id


def test_photoslibrary_make_album_folders_bad_album(
    photoslib: photoscript.PhotosLibrary,
):
    """test make_album_folders with missing album name"""
    with pytest.raises(ValueError):
        assert photoslib.make_album_folders(None, ["Folder1"])


def test_photoslibrary_make_album_folders_bad_folder_path(
    photoslib: photoscript.PhotosLibrary,
):
    """test make_album_folders with bad folder path"""
    with pytest.raises(TypeError):
        assert photoslib.make_album_folders("New Album", "Folder1")

    with pytest.raises(ValueError):
        assert photoslib.make_album_folders("New Album", [])


def test_photoslibrary_delete_folder(photoslib: photoscript.PhotosLibrary):
    """test delete folder"""
    photoslib.delete_folder(photoslib.folder("Travel"))
    assert "Travel" not in photoslib.folder_names(top_level=False)


def test_photoslibrary_delete_folder_tree(photoslib: photoscript.PhotosLibrary):
    """test delete folder tree"""

    global FOLDER_NAMES_ALL, FOLDER_NAMES_TOP

    photoslib.delete_folder(photoslib.folder("Folder1"))
    folders = photoslib.folder_names(top_level=False)
    assert "Folder1" not in folders
    assert "SubFolder1" not in folders

    # set up for next test
    FOLDER_NAMES_ALL = [
        x for x in FOLDER_NAMES_ALL if x not in ["Folder1", "SubFolder1"]
    ]
    FOLDER_NAMES_TOP = [x for x in FOLDER_NAMES_TOP if x != "Folder1"]


def test_photoslibrary_selection_none(photoslib: photoscript.PhotosLibrary):
    """test .selection() with no selection"""
    sel = photoslib.selection
    assert sel == []


def test_photoslibrary_len(photoslib: photoscript.PhotosLibrary):
    # account for photos imported during tests in this file
    assert len(photoslib) == NUM_PHOTOS + 3


def test_temp_album_name(photoslib: photoscript.PhotosLibrary):
    temp_name = photoslib._temp_album_name()
    assert temp_name not in photoslib.album_names(top_level=False)


def test_temp_album_name_2(photoslib: photoscript.PhotosLibrary):
    """test _temp_album_name when album name exists"""

    def make_temp_name_func():
        count = 0

        def temp_name(*args):
            nonlocal count
            count += 1
            return f"New Album {count}"

        return temp_name

    old_temp_name = photoslib._temp_name
    photoslib._temp_name = make_temp_name_func()
    photoslib.create_album(
        "New Album 1"
    )  # will cause conflict with redefined _temp_name
    temp_name = photoslib._temp_album_name()
    assert temp_name not in photoslib.album_names(top_level=False)
    photoslib._temp_name = old_temp_name


def test_temp_name(photoslib: photoscript.PhotosLibrary):
    temp_name = photoslib._temp_name()
    assert temp_name.startswith("photoscript_20")


def test_export_photo_basic(photoslib: photoscript.PhotosLibrary):

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTO_EXPORT_UUID)
    exported = photoslib._export_photo(photo, tmpdir.name)
    exported = [pathlib.Path(filename).name for filename in exported]
    assert exported == PHOTO_EXPORT_FILENAME
    files = os.listdir(tmpdir.name)
    assert files == PHOTO_EXPORT_FILENAME


def test_export_photo_bad_path(photoslib: photoscript.PhotosLibrary):

    photo = photoscript.Photo(PHOTO_EXPORT_UUID)
    with pytest.raises(ValueError):
        photoslib._export_photo(photo, photoslib._temp_name())


def test_export_photo_duplicate(photoslib: photoscript.PhotosLibrary):
    """Test calling export twice resulting in
    duplicate filenames"""

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTO_EXPORT_UUID)
    exported1 = photoslib._export_photo(photo, tmpdir.name)
    exported2 = photoslib._export_photo(photo, tmpdir.name)
    exported = [pathlib.Path(filename).name for filename in exported1 + exported2]
    assert exported == PHOTO_EXPORT_2_FILENAMES
    files = os.listdir(tmpdir.name)
    assert files == PHOTO_EXPORT_2_FILENAMES


def test_export_photo_duplicate_overwrite(photoslib: photoscript.PhotosLibrary):
    """Test calling export twice resulting in
    duplicate filenames but use overwrite = true"""

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTO_EXPORT_UUID)
    exported1 = photoslib._export_photo(photo, tmpdir.name)
    exported2 = photoslib._export_photo(photo, tmpdir.name, overwrite=True)
    exported = list({pathlib.Path(filename).name for filename in exported1 + exported2})

    assert exported == PHOTO_EXPORT_FILENAME
    files = os.listdir(tmpdir.name)
    assert files == PHOTO_EXPORT_FILENAME


def test_export_photo_original_basic(photoslib: photoscript.PhotosLibrary):

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTO_EXPORT_UUID)
    exported = photoslib._export_photo(photo, tmpdir.name, original=True)
    exported = [pathlib.Path(filename).name for filename in exported]
    # on Ventura, JPG is exported as .JPG, but on Catalina, it's .jpeg
    # so just look at the stem
    assert stemset(exported) == stemset(PHOTO_EXPORT_FILENAME_ORIGINAL)
    files = os.listdir(tmpdir.name)
    assert stemset(files) == stemset(PHOTO_EXPORT_FILENAME_ORIGINAL)


def test_export_photo_original_duplicate(photoslib: photoscript.PhotosLibrary):
    """Test calling export twice resulting in
    duplicate filenames"""

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTO_EXPORT_UUID)
    exported1 = photoslib._export_photo(photo, tmpdir.name, original=True)
    exported2 = photoslib._export_photo(photo, tmpdir.name, original=True)
    exported = [pathlib.Path(filename).name for filename in exported1 + exported2]
    assert stemset(exported) == stemset(PHOTO_EXPORT_2_FILENAMES_ORIGINAL)
    files = os.listdir(tmpdir.name)
    assert stemset(files) == stemset(PHOTO_EXPORT_2_FILENAMES_ORIGINAL)


def test_export_photo_original_duplicate_overwrite(
    photoslib: photoscript.PhotosLibrary,
):
    """Test calling export twice resulting in
    duplicate filenames but use overwrite = true"""

    tmpdir = tempfile.TemporaryDirectory(prefix="photoscript_test_")

    photo = photoscript.Photo(PHOTO_EXPORT_UUID)
    exported1 = photoslib._export_photo(photo, tmpdir.name, original=True)
    exported2 = photoslib._export_photo(
        photo, tmpdir.name, original=True, overwrite=True
    )
    exported = list({pathlib.Path(filename).name for filename in exported1 + exported2})

    assert stemset(exported) == stemset(PHOTO_EXPORT_FILENAME_ORIGINAL)
    files = os.listdir(tmpdir.name)
    assert stemset(files) == stemset(PHOTO_EXPORT_FILENAME_ORIGINAL)


def test_version():
    """test photoscript/_version.py"""
    from photoscript._version import __version__

    assert __version__


def test_script_loader_load_applescript():

    script = photoscript.script_loader.load_applescript("photoscript")
    assert isinstance(script, AppleScript)


def test_script_loader_load_applescript_bad_script():

    with pytest.raises(ValueError):
        photoscript.script_loader.load_applescript("BAD_SCRIPT")
