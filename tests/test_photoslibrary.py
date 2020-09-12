""" Test PhotosLibrary class """

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


def test_photoslibrary_import_photos_dup_check(photoslib):
    """ Attempt to import a duplicate photo with skip_duplicate_check = False
        This will cause Photos to display dialog box prompting user what to do """
    import os
    import pathlib

    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photoslib.import_photos(photo_paths)
    photos = photoslib.photos()
    assert len(photos) == NUM_PHOTOS + 1

    # Photos will block waiting for user to act on dialog box
    prompt = "Click Don't Import in Photos after the drop down sheet appears."
    os.system(f'say "{prompt}"')
    photos = photoslib.import_photos(photo_paths)
    assert not photos
    photos = photoslib.photos()
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


########## Non-interactive tests ##########


def test_photoslibrary_activate(photoslib):
    import photoscript

    photoslib.activate()
    assert photoslib.frontmost


def test_photoslibrary_quit(photoslib):
    import photoscript
    from applescript import AppleScript

    photoslib.quit()
    script = AppleScript(
        """
            on is_running(appName)
                tell application "System Events" to (name of processes) contains appName
            end is_running
        """
    )
    assert not script.call("is_running", "Photos")


def test_photoslibrary_running(photoslib):
    import time

    assert photoslib.running
    photoslib.quit()
    time.sleep(3)  # give photos time to quit
    assert not photoslib.running


def test_photoslibrary_hide(photoslib):
    photoslib.activate()
    assert photoslib.frontmost
    photoslib.hide()
    assert not photoslib.frontmost


def test_photoslibrary_hidden(photoslib):
    photoslib.activate()
    assert not photoslib.hidden
    photoslib.hide()
    assert photoslib.hidden


def test_photoslibrary_name(photoslib):
    assert photoslib.name == "Photos"


def test_photoslibrary_version(photoslib):
    import platform

    os_ver = get_os_version()[1]
    photo_ver = photoslib.version

    if os_ver == "12":
        assert photo_ver == "2.0"
    elif os_ver == "13":
        assert photo_ver == "3.0"
    elif os_ver == "14":
        assert photo_ver == "4.0"
    elif os_ver == "15":
        assert photo_ver == "5.0"
    elif os_ver == "16":
        assert photo_ver == "6.0"
    else:
        assert False


def test_photoslibrary_frontmost(photoslib):
    import photoscript

    photoslib.activate()
    assert photoslib.frontmost

    script = AppleScript(
        """
            tell application "Finder" to activate
            delay 2
        """
    )
    script.run()
    assert not photoslib.frontmost


def test_photoslibrary_favorites(photoslib):
    import photoscript

    favorites = photoslib.favorites
    fav_names = [photo.filename for photo in favorites.photos()]
    assert sorted(fav_names) == sorted(PHOTOS_FAVORITES)

    # set/unset favorites and check again
    photo = photoslib.photos(uuid=[PHOTO_FAVORITES_SET_UUID])[0]
    photo.favorite = True
    photo = photoslib.photos(uuid=[PHOTO_FAVORITES_UNSET_UUID])[0]
    photo.favorite = False

    favorites = photoslib.favorites
    fav_names = [photo.filename for photo in favorites.photos()]
    assert sorted(fav_names) == sorted(PHOTOS_FAVORITES_SET)


def test_photoslibrary_photos_no_args(photoslib):
    photos = photoslib.photos()
    assert len(photos) == 5
    filenames = [photo.filename for photo in photos]
    assert sorted(filenames) == sorted(PHOTOS_FILENAMES)


def test_photoslibrary_photos_search(photoslib):
    photos = photoslib.photos(search="plants")
    assert len(photos) == len(PHOTOS_PLANTS)
    filenames = [photo.filename for photo in photos]
    assert sorted(filenames) == sorted(PHOTOS_PLANTS)


def test_photoslibrary_photos_uuid(photoslib):
    photos = photoslib.photos(uuid=PHOTOS_UUID)
    assert len(photos) == len(PHOTOS_UUID)
    filenames = [photo.filename for photo in photos]
    assert sorted(filenames) == sorted(PHOTOS_UUID_FILENAMES)


def test_photoslibrary_photos_exception(photoslib):
    with pytest.raises(ValueError):
        photoslib.photos(uuid=PHOTOS_UUID, search="plants")


def test_photoslibrary_import_photos(photoslib):
    import os
    import pathlib

    import photoscript

    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photos = photoslib.import_photos(photo_paths)
    assert isinstance(photos[0], photoscript.Photo)
    filenames = [photo.filename for photo in photos]
    assert filenames == IMPORT_PHOTOS


def test_photoslibrary_import_photos_skip_dup_check(photoslib):
    """ Attempt to import a duplicate photo with skip_duplicate_check = True
        This will cause a duplicate photo to be imported """
    import os
    import pathlib

    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photoslib.import_photos(photo_paths)
    photos = photoslib.photos()
    assert len(photos) == NUM_PHOTOS + 1
    photoslib.import_photos(photo_paths, skip_duplicate_check=True)
    photos = photoslib.photos()
    assert len(photos) == NUM_PHOTOS + 2


def test_photoslibrary_import_photos_album(photoslib):
    import os
    import pathlib

    album = photoslib.create_album("New Album")
    cwd = os.getcwd()
    photo_paths = [str(pathlib.Path(cwd) / path) for path in IMPORT_PATHS]
    photoslib.import_photos(photo_paths, album=album)
    photos = album.photos()
    filenames = [photo.filename for photo in photos]
    for filename in IMPORT_PHOTOS:
        assert filename in filenames


def test_photoslibrary_album_names(photoslib):
    import photoscript

    albums = photoslib.album_names()
    assert sorted(albums) == sorted(ALBUM_NAMES_ALL)


def test_photoslibrary_album_names_top(photoslib):
    import photoscript

    albums = photoslib.album_names(top_level=True)
    assert sorted(albums) == sorted(ALBUM_NAMES_TOP)


def test_photoslibrary_folder_names(photoslib):
    import photoscript

    folders = photoslib.folder_names()
    assert sorted(folders) == sorted(FOLDER_NAMES_ALL)


def test_photoslibrary_folder_names_top(photoslib):
    import photoscript

    folders = photoslib.folder_names(top_level=True)
    assert sorted(folders) == sorted(FOLDER_NAMES_TOP)


def test_photoslibrary_album_by_name(photoslib):
    import photoscript

    album = photoslib.album(ALBUM_1_NAME)
    assert album is not None
    assert isinstance(album, photoscript.Album)


def test_photoslibrary_album_by_uuid(photoslib):
    import photoscript

    album = photoslib.album(uuid=ALBUM_1_UUID)
    assert album is not None
    assert isinstance(album, photoscript.Album)


def test_photoslibrary_album_bad_name(photoslib):

    album = photoslib.album("BAD_NAME")
    assert album is None


def test_photoslibrary_album_bad_uuid(photoslib):

    with pytest.raises(ValueError):
        photoslib.album(uuid="BAD_UUID")


def test_photoslibrary_album_exception_1(photoslib):
    with pytest.raises(ValueError):
        photoslib.album()


def test_photoslibrary_album_exception_2(photoslib):
    with pytest.raises(ValueError):
        photoslib.album(ALBUM_1_NAME, uuid=ALBUM_1_UUID)


def test_photoslibrary_albums(photoslib):
    albums = photoslib.albums()
    assert len(albums) == len(ALBUM_NAMES_ALL)
    album_names = [album.name for album in albums]
    assert sorted(album_names) == sorted(ALBUM_NAMES_ALL)


def test_photoslibrary_albums_top(photoslib):
    albums = photoslib.albums(top_level=True)
    assert len(albums) == len(ALBUM_NAMES_TOP)
    album_names = [album.name for album in albums]
    assert sorted(album_names) == sorted(ALBUM_NAMES_TOP)


def test_photoslibrary_create_album(photoslib):
    import photoscript

    album = photoslib.create_album("New Album")
    assert isinstance(album, photoscript.Album)

    albums = photoslib.album_names()
    assert "New Album" in albums


def test_photoslibrary_create_album_error(photoslib):
    import os
    import pathlib
    import photoscript

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_album("New Album")
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_create_album_at_folder(photoslib):
    import photoscript

    album = photoslib.create_album(
        "New Album In Folder", folder=photoslib.folder("Folder1", top_level=True)
    )
    assert isinstance(album, photoscript.Album)

    albums = photoslib.album_names()
    assert "New Album In Folder" in albums

    assert album.parent.name == "Folder1"


def test_photoslibrary_create_album_at_folder_error(photoslib):
    import os
    import pathlib
    import photoscript

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    folder = photoslib.folder("Folder1")
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_album("New Album", folder=folder)
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_delete_album(photoslib):
    import photoscript

    album = photoslib.album("Farmers Market")
    photoslib.delete_album(album)
    assert "Farmers Market" not in photoslib.album_names()


def test_photoslibrary_folder(photoslib):
    import photoscript

    folder = photoslib.folder("Folder1")
    assert isinstance(folder, photoscript.Folder)
    subfolders = folder.subfolders
    assert len(subfolders) == 1
    assert subfolders[0].name == "SubFolder1"


def test_photoslibrary_folder_top_level(photoslib):
    import photoscript

    folder = photoslib.folder("SubFolder1", top_level=True)
    assert folder is None


def test_photoslibrary_folder_exception_1(photoslib):
    """ test exceptions in folder() """
    import photoscript

    with pytest.raises(ValueError):
        folder = photoslib.folder()


def test_photoslibrary_folder_exception_2(photoslib):
    """ test exceptions in folder() """
    import photoscript

    with pytest.raises(ValueError):
        folder = photoslib.folder("Travel", uuid=FOLDER_UUID)


def test_photoslibrary_folder_by_uuid(photoslib):
    """ test getting folder by UUID """
    import photoscript

    folder = photoslib.folder(uuid=FOLDER_UUID)
    assert isinstance(folder, photoscript.Folder)
    assert folder.name == FOLDER_NAME


def test_photoslibrary_folder_bad_uuid(photoslib):
    """ test getting folder by invalid UUID """
    with pytest.raises(ValueError):
        photoslib.folder(uuid="BAD_UUID")


def test_photoslibrary_folder_by_path_1(photoslib):
    import photoscript

    folder = photoslib.folder_by_path(["Travel"])
    assert isinstance(folder, photoscript.Folder)


def test_photoslibrary_folder_by_path_2(photoslib):
    import photoscript

    folder = photoslib.folder_by_path(["Folder1", "SubFolder1"])
    assert isinstance(folder, photoscript.Folder)


def test_photoslibrary_folder_by_path_bad_path(photoslib):
    import photoscript

    folder = photoslib.folder_by_path(["Folder1", "SubFolder1", "I Don't Exist"])
    assert folder is None


def test_photoslibrary_folders_top_level(photoslib):
    folders = photoslib.folders()
    folder_names = [folder.name for folder in folders]
    assert sorted(folder_names) == sorted(FOLDER_NAMES_TOP)


def test_photoslibrary_folders_all(photoslib):
    folders = photoslib.folders(top_level=False)
    folder_names = [folder.name for folder in folders]
    assert sorted(folder_names) == sorted(FOLDER_NAMES_ALL)


def test_photoslibrary_create_folder(photoslib):
    import photoscript

    folder = photoslib.create_folder("New Folder")
    assert isinstance(folder, photoscript.Folder)

    folders = photoslib.folder_names()
    assert "New Folder" in folders


def test_photoslibrary_create_folder_error(photoslib):
    import os
    import pathlib
    import photoscript

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_folder("New Folder")
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_create_folder_at_folder(photoslib):
    import photoscript

    folder = photoslib.create_folder("New SubFolder", folder=photoslib.folder("Travel"))
    assert isinstance(folder, photoscript.Folder)

    folders = photoslib.folder_names(top_level=True)
    assert "New SubFolder" not in folders

    folders = photoslib.folder_names()
    assert "New SubFolder" in folders

    assert folder.parent.name == "Travel"


def test_photoslibrary_create_folder_at_folder_error(photoslib):
    import os
    import pathlib
    import photoscript

    folder = photoslib.folder("Travel")

    script_obj = photoscript.script_loader.SCRIPT_OBJ
    mock_script = pathlib.Path(os.getcwd()) / "tests" / "mock_photoscript"
    photoscript.script_loader.SCRIPT_OBJ = photoscript.script_loader.load_applescript(
        mock_script
    )
    with pytest.raises(photoscript.AppleScriptError):
        photoslib.create_folder("New Folder", folder=folder)
    photoscript.script_loader.SCRIPT_OBJ = script_obj


def test_photoslibrary_make_folders_exist(photoslib):
    """ test make_folders with path that exists """
    import photoscript

    subfolder = photoslib.folder("SubFolder1", top_level=False)
    folder = photoslib.make_folders(["Folder1", "SubFolder1"])
    assert isinstance(folder, photoscript.Folder)
    assert len(photoslib.folders(top_level=False)) == len(FOLDER_NAMES_ALL)
    assert subfolder.id == folder.id


def test_photoslibrary_make_folders_new(photoslib):
    """ test make_folders with entirely new path """
    import photoscript

    folder = photoslib.make_folders(["Folder2", "SubFolder2"])
    assert isinstance(folder, photoscript.Folder)
    assert len(photoslib.folders(top_level=False)) == len(FOLDER_NAMES_ALL) + 2


def test_photoslibrary_make_folders_new_exist(photoslib):
    """ test make_folders with new path inside existing path"""
    import photoscript

    subfolder = photoslib.folder("SubFolder1", top_level=False)
    folder = photoslib.make_folders(["Folder1", "SubFolder1", "New Sub Folder"])
    assert isinstance(folder, photoscript.Folder)
    assert len(photoslib.folders(top_level=False)) == len(FOLDER_NAMES_ALL) + 1
    assert folder.parent_id == subfolder.id


def test_photoslibrary_make_folders_bad_type(photoslib):
    """ test make_folders with non-list value for folders """
    with pytest.raises(TypeError):
        photoslib.make_folders("Folder1")


def test_photoslibrary_make_folders_bad_value(photoslib):
    """ test make_folders with empty value for folders """
    with pytest.raises(ValueError):
        photoslib.make_folders([])


def test_photoslibrary_make_album_folders_new_path(photoslib):
    """ test make_album_folders with new path """
    import photoscript

    album = photoslib.make_album_folders("New Album", ["Folder2", "SubFolder2"])
    assert isinstance(album, photoscript.Album)
    assert "New Album" in photoslib.album_names(top_level=False)


def test_photoslibrary_make_album_folders_new_album(photoslib):
    """ test make_album_folders with new album in existing folder """
    import photoscript

    album = photoslib.make_album_folders("New Album", ["Folder1", "SubFolder1"])
    assert isinstance(album, photoscript.Album)
    assert "New Album" in photoslib.album_names(top_level=False)


def test_photoslibrary_make_album_folders_existing_album(photoslib):
    """ test make_album_folders with new album in existing folder """
    import photoscript

    album = photoslib.album("San Juan Capistrano")
    new_album = photoslib.make_album_folders("San Juan Capistrano", ["Travel"])
    assert isinstance(album, photoscript.Album)
    assert album.id == new_album.id


def test_photoslibrary_make_album_folders_bad_album(photoslib):
    """ test make_album_folders with missing album name """
    with pytest.raises(ValueError):
        assert photoslib.make_album_folders(None, ["Folder1"])


def test_photoslibrary_make_album_folders_bad_folder_path(photoslib):
    """ test make_album_folders with bad folder path """
    with pytest.raises(TypeError):
        assert photoslib.make_album_folders("New Album", "Folder1")

    with pytest.raises(ValueError):
        assert photoslib.make_album_folders("New Album", [])


def test_photoslibrary_delete_folder(photoslib):
    """ test delete folder """
    photoslib.delete_folder(photoslib.folder("Travel"))
    assert "Travel" not in photoslib.folder_names(top_level=False)


def test_photoslibrary_delete_folder_tree(photoslib):
    """ test delete folder tree """
    photoslib.delete_folder(photoslib.folder("Folder1"))
    folders = photoslib.folder_names(top_level=False)
    assert "Folder1" not in folders
    assert "SubFolder1" not in folders


def test_photoslibrary_selection_none(photoslib):
    """ test .selection() with no selection """
    sel = photoslib.selection
    assert sel == []


def test_photoslibrary_len(photoslib):
    assert len(photoslib) == NUM_PHOTOS


def test_temp_album_name(photoslib):
    temp_name = photoslib._temp_album_name()
    assert temp_name not in photoslib.album_names(top_level=False)


def test_temp_album_name_2(photoslib):
    """ test _temp_album_name when album name exists """

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


def test_temp_name(photoslib):
    temp_name = photoslib._temp_name()
    assert temp_name.startswith("photoscript_20")


def test_version():
    """ test photoscript/_version.py """
    from photoscript._version import __version__

    assert __version__


def test_script_loader_load_applescript():
    import photoscript
    from applescript import AppleScript

    script = photoscript.script_loader.load_applescript("photoscript")
    assert isinstance(script, AppleScript)


def test_script_loader_load_applescript_bad_script():
    import photoscript

    with pytest.raises(ValueError):
        photoscript.script_loader.load_applescript("BAD_SCRIPT")
