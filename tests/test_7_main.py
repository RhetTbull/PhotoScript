""" Test __main__ """

import pytest
from applescript import AppleScript
from tests.conftest import photoslib, suspend_capture, get_os_version

OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import PHOTOS_DICT
else:
    pytest.exit("This test suite currently only runs on MacOS Catalina ")

def test_main(photoslib, monkeypatch, capsys):
    import io
    from photoscript.__main__ import main
    monkeypatch.setattr('sys.stdin', io.StringIO('photos = photoslib.photos()\nlen(photos)\n'))
    main()
    captured = capsys.readouterr()
    assert "Variables defined: photoslib" in captured.err
    assert "5" in captured.out