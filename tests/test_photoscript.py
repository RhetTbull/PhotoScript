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


def test_photoslibrary_album_names(photoslib):
    import photoscript


    albums = photoslib.album_names()
    assert sorted(albums) == sorted(ALBUM_NAMES_ALL)


def test_photoslibrary_album_names_top(photoslib):
    import photoscript


    albums = photoslib.album_names(top_level=True)
    assert sorted(albums) == sorted(ALBUM_NAMES_TOP)

# def test_photoslibrary_create_album(photoslib):
#     import photoscript
    
#     album = photoslib.create_album("New Album")
#     assert isinstance(album, photoscript.Album)

#     albums = photoslib.album_names()
#     assert sorted(albums) == sorted(ALBUM_NAMES_ALL+["New Album"])


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
    uuids = [photo.uuid for photo in sel]
    assert sorted(uuids) == sorted(SELECTION_UUIDS)

