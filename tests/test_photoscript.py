import pytest

from tests.conftest import photoslib, suspend_capture
from applescript import AppleScript

ALBUM_1_NAME = "San Juan Capistrano"
ALBUM_1_UUID = "01F18AB8-B0D7-4414-96A8-28D94AFE86BF/L0/040"
SELECTION_UUIDS = [
    "3A71DE26-EDEF-41D3-86C1-E8328DFC9FA0/L0/001",
    "B6DB996D-8A0A-4983-AFBD-D206B7D38A23/L0/001",
]
ALBUM_NAMES_ALL = ["Empty Album", "Farmers Market", "San Juan Capistrano"]
ALBUM_NAMES_TOP = ["Empty Album", "Farmers Market"]
FOLDER_NAMES_ALL = ["Travel", "Folder1", "SubFolder1"]
FOLDER_NAMES_TOP = ["Travel", "Folder1"]

PHOTOS_FAVORITES = ["IMG_2510.JPG", "IMG_2768.JPG"]
PHOTOS_FAVORITES_SET = ["IMG_2242.JPG", "IMG_2510.JPG"]
PHOTO_FAVORITES_SET_UUID = "1CD1B172-C94B-4093-A303-EE24FE7EEF60/L0/001"
PHOTO_FAVORITES_UNSET_UUID = "EECD91FE-D716-48F2-A62C-A4D558ACD52E/L0/001"

NUM_PHOTOS = 5  # total number of photos in test library

PHOTOS_FILENAMES = [
    "IMG_2242.JPG",
    "IMG_2510.JPG",
    "IMG_2768.JPG",
    "IMG_2774.JPG",
    "IMG_0096.jpeg",
]
PHOTOS_UUID = [
    "B6DB996D-8A0A-4983-AFBD-D206B7D38A23/L0/001",
    "EECD91FE-D716-48F2-A62C-A4D558ACD52E/L0/001",
]
PHOTOS_UUID_FILENAMES = ["IMG_2510.JPG", "IMG_2768.JPG"]
PHOTOS_PLANTS = ["IMG_2242.JPG"]
FOLDER_UUID = "3205FEEF-B22D-43D6-8D31-9A4D112B67E3/L0/020"  # Travel
FOLDER_NAME = "Travel"

IMPORT_PATHS = ["tests/test_images/IMG_2608.JPG"]
IMPORT_PHOTOS = ["IMG_2608.JPG"]


def get_os_version():
    import platform

    # returns tuple containing OS version
    # e.g. 10.13.6 = (10, 13, 6)
    version = platform.mac_ver()[0].split(".")
    if len(version) == 2:
        (ver, major) = version
        minor = "0"
    elif len(version) == 3:
        (ver, major, minor) = version
    else:
        raise (
            ValueError(
                f"Could not parse version string: {platform.mac_ver()} {version}"
            )
        )
    return (ver, major, minor)


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


def test_photoslibrary_create_album_at_folder(photoslib):
    import photoscript

    album = photoslib.create_album(
        "New Album In Folder", folder=photoslib.folder("Folder1", top_level=True)
    )
    assert isinstance(album, photoscript.Album)

    albums = photoslib.album_names()
    assert "New Album In Folder" in albums

    assert album.parent.name == "Folder1"


def test_photoslibrary_delete_album(photoslib):
    import photoscript

    album = photoslib.album("Farmers Market")
    photoslib.delete_album(album)
    assert "Farmers Market" not in photoslib.album_names()


def test_photoslibrary_folder(photoslib):
    import photoscript

    folder = photoslib.folder("Folder1")
    assert isinstance(folder, photoscript.Folder)
    subfolders = folder.folders
    assert len(subfolders) == 1
    assert subfolders[0].name == "SubFolder1"


def test_photoslibrary_folder_top_level(photoslib):
    import photoscript

    folder = photoslib.folder("SubFolder1", top_level=True)
    assert folder is None


def test_photoslibrary_folder_exception(photoslib):
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


# TODO: this test fails
# def test_photoscript_folder_bad_uuid(photoslib):
#     """ test getting folder by invalid UUID """
#     with pytest.raises(ValueError):
#         photoslib.folder(uuid="BAD_UUID")


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


def test_photoslibrary_create_folder_at_folder(photoslib):
    import photoscript

    folder = photoslib.create_folder("New SubFolder", folder=photoslib.folder("Travel"))
    assert isinstance(folder, photoscript.Folder)

    folders = photoslib.folder_names(top_level=True)
    assert "New SubFolder" not in folders

    folders = photoslib.folder_names()
    assert "New SubFolder" in folders

    assert folder.parent.name == "Travel"


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

