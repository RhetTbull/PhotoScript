import os
import pathlib
import shutil
import subprocess
import sys

import pytest
from applescript import AppleScript

import photoscript

TEST_LIBRARY = "Test-PhotoScript-10.15.6.photoslibrary"


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


def ditto(src, dest, norsrc=False):
    """ Copies a file or directory tree from src path to dest path 
        src: source path as string 
        dest: destination path as string
        norsrc: (bool) if True, uses --norsrc flag with ditto so it will not copy
                resource fork or extended attributes.  May be useful on volumes that
                don't work with extended attributes (likely only certain SMB mounts)
                default is False
        Uses ditto to perform copy; will silently overwrite dest if it exists
        Raises exception if copy fails or either path is None """

    if src is None or dest is None:
        raise ValueError("src and dest must not be None", src, dest)

    if norsrc:
        command = ["/usr/bin/ditto", "--norsrc", src, dest]
    else:
        command = ["/usr/bin/ditto", src, dest]

    # if error on copy, subprocess will raise CalledProcessError
    result = subprocess.run(command, check=True, stderr=subprocess.PIPE)

    return result.returncode


def copy_photos_library(delay=0):
    """ copy the test library and open Photos """
    script = AppleScript(
        """
        tell application "Photos"
            quit
        end tell
        """
    )
    script.run()
    src = pathlib.Path(os.getcwd()) / f"tests/test_libraries/{TEST_LIBRARY}"
    picture_folder = (
        pathlib.Path(os.environ["PHOTOSCRIPT_PICTURES_FOLDER"])
        if "PHOTOSCRIPT_PICTURES_FOLDER" in os.environ
        else pathlib.Path("~/Pictures")
    )
    picture_folder = picture_folder.expanduser()
    if not picture_folder.is_dir():
        pytest.exit(f"Invalid picture folder: '{picture_folder}'")
    dest = picture_folder / TEST_LIBRARY
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
