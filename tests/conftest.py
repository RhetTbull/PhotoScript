import os
import pathlib

import pytest
from applescript import AppleScript

import photoscript
from photoscript.utils import ditto


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


OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import TEST_LIBRARY
else:
    TEST_LIBRARY = None
    pytest.exit("This test suite currently only runs on MacOS Catalina ")


def copy_photos_library(photos_library=TEST_LIBRARY, delay=0):
    """ copy the test library and open Photos, returns path to copied library """
    script = AppleScript(
        """
        tell application "Photos"
            quit
        end tell
        """
    )
    script.run()
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
    ditto(src, dest)
    script = AppleScript(
        f"""
            set tries to 0
            repeat while tries < 5
                try
                    tell application "Photos"
                        activate
                        delay 3 
                        open POSIX file "{dest}"
                        delay {delay}
                    end tell
                    set tries to 5
                on error
                    set tries to tries + 1
                end try
            end repeat
        """
    )
    script.run()
    return dest


@pytest.fixture(scope="session", autouse=True)
def setup_photos():
    copy_photos_library(delay=10)


# @pytest.fixture(scope="session")
@pytest.fixture
def photoslib():
    copy_photos_library()
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
