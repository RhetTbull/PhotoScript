"""Utility functions for photoscript"""

from __future__ import annotations

import fnmatch
import os
import platform
import re
import subprocess


def ditto(src, dest, norsrc=False):
    """Copies a file or directory tree from src path to dest path
    src: source path as string
    dest: destination path as string
    norsrc: (bool) if True, uses --norsrc flag with ditto so it will not copy
            resource fork or extended attributes.  May be useful on volumes that
            don't work with extended attributes (likely only certain SMB mounts)
            default is False
    Uses ditto to perform copy; will silently overwrite dest if it exists
    Raises exception if copy fails or either path is None"""

    if src is None or dest is None:
        raise ValueError("src and dest must not be None", src, dest)

    if norsrc:
        command = ["/usr/bin/ditto", "--norsrc", src, dest]
    else:
        command = ["/usr/bin/ditto", src, dest]

    # if error on copy, subprocess will raise CalledProcessError
    result = subprocess.run(command, check=True, stderr=subprocess.PIPE)

    return result.returncode


def findfiles(pattern, path_):
    """Returns list of filenames from path_ matched by pattern
    shell pattern. Matching is case-insensitive.
    If 'path_' is invalid/doesn't exist, returns []."""
    if not os.path.isdir(path_):
        return []
    # See: https://gist.github.com/techtonik/5694830

    rule = re.compile(fnmatch.translate(pattern), re.IGNORECASE)
    return [name for name in os.listdir(path_) if rule.match(name)]


def get_os_version() -> tuple[int, int, int]:
    # returns tuple of str containing OS version
    # e.g. 10.13.6 = ("10", "13", "6")
    version = platform.mac_ver()[0].split(".")
    if len(version) == 2:
        (ver, major) = version
        minor = 0
    elif len(version) == 3:
        (ver, major, minor) = version
    else:
        raise (
            ValueError(
                f"Could not parse version string: {platform.mac_ver()} {version}"
            )
        )
    return int(ver), int(major), int(minor)


def uuid_from_error_str(error: str) -> str | None:
    """Return UUID for a photo from an AppleScript error string"""
    # Sometimes AppleScript generates an error like:
    # photoscript.exceptions.AppleScriptError: run_script 'photosLibraryGetSelection' failed: Photos got an error: Can’t get media item id "EC19EA1A-FC91-449C-8925-B13D863E2EDB/L0/001" of album id "4DE59C3F-2D8A-4E3F-AFA0-0C48BCDB75DD/L0/040". (-1728) app='Photos' range=22182-22235
    # In these cases, try to get the UUID from the error string using regex matching, otherwise return None
    match = re.search(r'media item id "(.*?)"', error)
    if match:
        try:
            # return only the UUID part before /L0/001
            uuid = match.group(1).split("/")[0]
            return uuid
        except IndexError:
            return None
    return None
