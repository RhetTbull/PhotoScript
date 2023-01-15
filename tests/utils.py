"""Utility functions for tests"""

from __future__ import annotations

import pathlib


def stemset(filepaths: list[str]) -> set[str]:
    """ "Return set of filename stems of filepaths"""
    # return set instead of list for easier comparison regardless of order
    return {pathlib.Path(filepath).stem for filepath in filepaths}
