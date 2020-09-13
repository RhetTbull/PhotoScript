""" Utility functions for photoscript """

import fnmatch
import os
import re
import subprocess


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


def findfiles(pattern, path_):
    """Returns list of filenames from path_ matched by pattern
       shell pattern. Matching is case-insensitive.
       If 'path_' is invalid/doesn't exist, returns []."""
    if not os.path.isdir(path_):
        return []
    # See: https://gist.github.com/techtonik/5694830

    rule = re.compile(fnmatch.translate(pattern), re.IGNORECASE)
    return [name for name in os.listdir(path_) if rule.match(name)]
