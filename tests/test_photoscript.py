from tests.conftest import photoslib, suspend_capture
import pytest

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

FOLDER_UUID = "3205FEEF-B22D-43D6-8D31-9A4D112B67E3/L0/020"  # Travel
FOLDER_NAME = "Travel"


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


def test_photoslibrary_frontmost(photoslib):
    import photoscript
    from applescript import AppleScript

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
    import photoscript

    album = photoslib.album("BAD_NAME")
    assert album is None


def test_photoslibrary_album_bad_uuid(photoslib):
    import photoscript

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


def test_photoslibrary_album_names(photoslib):
    import photoscript

    albums = photoslib.album_names()
    assert sorted(albums) == sorted(ALBUM_NAMES_ALL)


def test_photoslibrary_album_names_top(photoslib):
    import photoscript

    albums = photoslib.album_names(top_level=True)
    assert sorted(albums) == sorted(ALBUM_NAMES_TOP)


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


def test_photoslibrary_folder(photoslib):
    import photoscript

    folder = photoslib.folder("Folder1")
    assert isinstance(folder, photoscript.Folder)
    subfolders = folder.folders
    assert len(subfolders) == 1
    assert subfolders[0].name == "SubFolder1"


def test_photoscript_folder_top_level(photoslib):
    import photoscript

    folder = photoslib.folder("SubFolder1", top_level=True)
    assert folder is None


def test_photoscript_folder_exception(photoslib):
    """ test exceptions in folder() """
    import photoscript

    with pytest.raises(ValueError):
        folder = photoslib.folder("Travel", uuid=FOLDER_UUID)


def test_photoscript_folder_by_uuid(photoslib):
    """ test getting folder by UUID """
    import photoscript

    folder = photoslib.folder(uuid=FOLDER_UUID)
    assert isinstance(folder, photoscript.Folder)
    assert folder.name == FOLDER_NAME


def test_photoslibrary_delete_album(photoslib):
    import photoscript

    album = photoslib.album("Farmers Market")
    photoslib.delete_album(album)
    assert "Farmers Market" not in photoslib.album_names()


def test_photoslibrary_favorites(photoslib):
    import photoscript

    favorites = photoslib.favorites
    assert len(favorites) == len(PHOTOS_FAVORITES)
    fav_names = [photo.filename for photo in favorites.photos]
    assert sorted(fav_names) == sorted(PHOTOS_FAVORITES)


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

