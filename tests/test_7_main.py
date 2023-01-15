""" Test __main__ """

import pytest
from applescript import AppleScript

from tests.conftest import photoslib, suspend_capture
from tests.photoscript_config_data import PHOTOS_DICT


def test_main(photoslib, monkeypatch, capsys):
    import io

    from photoscript.__main__ import main
    monkeypatch.setattr('sys.stdin', io.StringIO('photos = [p for p in photoslib.photos()]\nlen(photos)\n'))
    main()
    captured = capsys.readouterr()
    assert "Variables defined: photoslib" in captured.err
    assert "5" in captured.out