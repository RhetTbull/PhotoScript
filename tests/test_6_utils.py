""" test utils.py """
import os
import pathlib
import tempfile

import pytest

from photoscript.utils import ditto, findfiles
from tests.conftest import photoslib, suspend_capture
from tests.photoscript_config_data import FIND_FILES


def test_ditto():
    tmpfile = tempfile.TemporaryDirectory(prefix="photoscript_")

    cwd = os.getcwd()
    src = pathlib.Path(cwd) / "tests/test_images/IMG_2608.JPG"
    ditto(src, tmpfile.name)
    dest = pathlib.Path(tmpfile.name) / "IMG_2608.JPG"
    assert dest.is_file()


def test_ditto_norsrc():
    tmpfile = tempfile.TemporaryDirectory(prefix="photoscript_")

    cwd = os.getcwd()
    src = pathlib.Path(cwd) / "tests/test_images/IMG_2608.JPG"
    ditto(src, tmpfile.name, norsrc=True)
    dest = pathlib.Path(tmpfile.name) / "IMG_2608.JPG"
    assert dest.is_file()


def test_ditto_exception():
    with pytest.raises(ValueError):
        ditto(None, None)


def test_findfiles():
    cwd = os.getcwd()
    dest = pathlib.Path(cwd) / "tests/test_images"
    files = findfiles("*.JPG", dest)
    assert sorted(files) == sorted(FIND_FILES)


def test_findfiles_bad_dir():
    files = findfiles("*.JPG", "BAD_DIR")
    assert files == []
