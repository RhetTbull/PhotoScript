import pytest

import shutil
from applescript import AppleScript
import os
import pathlib

TEST_LIBRARY = "Test-PhotoScript-10.15.6.photoslibrary"


@pytest.fixture(scope="session")
def photo_library():
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
    dest = os.path.expanduser(f"~/Pictures")
    library = shutil.copytree(src, dest, dirs_exist_ok=True)
    script = AppleScript(
        f"""
            set tries to 0
            repeat while tries < 5
                try
                    tell application "Photos"
                        activate
                        delay 5
                        open POSIX file "{library}"
                    end tell
                    set tries to 5
                on error
                    set tries to tries + 1
                end try
            end repeat
        """
    )
    script.run()
    return library

@pytest.fixture
def suspend_capture(pytestconfig):
    class suspend_guard:
        def __init__(self):
            self.capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')
        def __enter__(self):
            self.capmanager.suspend_global_capture(in_=True)
        def __exit__(self, _1, _2, _3):
            self.capmanager.resume_global_capture()

    yield suspend_guard()