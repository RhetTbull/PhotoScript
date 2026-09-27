import os
import pathlib
import shutil

import pytest
from applescript import AppleScript

import photoscript
# photoscript_config_data selects the test data (and library) for the running
# version of macOS and exits pytest if that version isn't supported
from tests.photoscript_config_data import TEST_LIBRARY


def copy_photos_library(photos_library=TEST_LIBRARY, open=True):
    """copy the test library and open Photos, returns path to copied library"""

    # quit Photos if it's running
    photoslib = photoscript.PhotosLibrary()
    photoslib.quit()

    src = pathlib.Path(os.getcwd()) / f"tests/test_libraries/{photos_library}"
    picture_folder = (
        pathlib.Path(os.environ["PHOTOSCRIPT_PICTURES_FOLDER"])
        if "PHOTOSCRIPT_PICTURES_FOLDER" in os.environ
        else pathlib.Path("~/Pictures")
    )
    picture_folder = picture_folder.expanduser()
    if not picture_folder.is_dir():
        pytest.exit(f"Invalid picture folder: '{picture_folder}'")
    dest = picture_folder / photos_library

    # copy src directory to dest directory, removing it if it already exists
    shutil.rmtree(dest, ignore_errors=True)

    copyFolder = AppleScript(
        """
        on copyFolder(sourceFolder, destinationFolder)
            -- sourceFolder and destinationFolder are strings of POSIX paths
            set sourceFolder to POSIX file sourceFolder
            set destinationFolder to POSIX file destinationFolder
            tell application "Finder"
                duplicate sourceFolder to destinationFolder
            end tell
        end copyFolder
        """
    )
    copyFolder.call("copyFolder", str(src), str(picture_folder))

    # open Photos
    if open:
        photoslib.open(str(dest))
    return dest


@pytest.fixture(scope="module", autouse=True)
def setup_photos():
    copy_photos_library()


@pytest.fixture
def photoslib():
    return photoscript.PhotosLibrary()


@pytest.fixture
def suspend_capture(pytestconfig):
    class suspend_guard:
        def __init__(self):
            self.capmanager = pytestconfig.pluginmanager.getplugin("capturemanager")

        def __enter__(self):
            self.capmanager.suspend_global_capture(in_=True)

        def __exit__(self, _1, _2, _3):
            self.capmanager.resume_global_capture()

    yield suspend_guard()
