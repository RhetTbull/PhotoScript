""" Test script_loader.py """

import pytest


def test_script_loader():
    import os

    from applescript import AppleScript
    import photoscript

    cwd = os.getcwd()

    script = photoscript.script_loader.load_applescript(
        os.path.join(cwd, "tests/applescript_test")
    )
    assert isinstance(script, AppleScript)
    assert script.call("test_applescript") == 42


def test_script_loader_bad_file():
    import photoscript

    with pytest.raises(ValueError):
        photoscript.script_loader.load_applescript("BAD_FILE")


def test_run_script():
    import os

    from applescript import AppleScript
    import photoscript

    cwd = os.getcwd()

    script = photoscript.script_loader.load_applescript(
        os.path.join(cwd, "tests/applescript_test")
    )
    old_script_obj = photoscript.script_loader.SCRIPT_OBJ
    photoscript.script_loader.SCRIPT_OBJ = script
    assert photoscript.script_loader.run_script("test_applescript") == 42
    photoscript.script_loader.SCRIPT_OBJ = old_script_obj

