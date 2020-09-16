""" test utils.py """
import pytest

from tests.conftest import photoslib, suspend_capture, get_os_version

OS_VER = get_os_version()[1]
if OS_VER == "15":
    from tests.photoscript_config_catalina import FIND_FILES
else:
    pytest.exit("This test suite currently only runs on MacOS Catalina ")


def test_ditto():
    import os
    import pathlib
    import tempfile

    from photoscript.utils import ditto

    tmpfile = tempfile.TemporaryDirectory(prefix="photoscript_")

    cwd = os.getcwd()
    src = pathlib.Path(cwd) / "tests/test_images/IMG_2608.JPG"
    ditto(src, tmpfile.name)
    dest = pathlib.Path(tmpfile.name) / "IMG_2608.JPG"
    assert dest.is_file()


def test_ditto_norsrc():
    import os
    import pathlib
    import tempfile

    from photoscript.utils import ditto

    tmpfile = tempfile.TemporaryDirectory(prefix="photoscript_")

    cwd = os.getcwd()
    src = pathlib.Path(cwd) / "tests/test_images/IMG_2608.JPG"
    ditto(src, tmpfile.name, norsrc=True)
    dest = pathlib.Path(tmpfile.name) / "IMG_2608.JPG"
    assert dest.is_file()


def test_ditto_exception():
    from photoscript.utils import ditto

    with pytest.raises(ValueError):
        ditto(None, None)


def test_findfiles():
    import os
    import pathlib

    from photoscript.utils import findfiles

    cwd = os.getcwd()
    dest = pathlib.Path(cwd) / "tests/test_images"
    files = findfiles("*.JPG", dest)
    assert sorted(files) == sorted(FIND_FILES)


def test_findfiles_bad_dir():
    import os
    import pathlib

    from photoscript.utils import findfiles

    files = findfiles("*.JPG", "BAD_DIR")
    assert files == []
