"""Test code snippets embedded in the docs.

Reference: https://sybil.readthedocs.io/en/latest/use.html#pytest
"""

import os
import tempfile
import zipfile
from doctest import ELLIPSIS, NORMALIZE_WHITESPACE

import pytest
from sybil import Sybil
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.skip import skip

from pylangacq.chat import _download_file


_REMOTE_BROWN_URL = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"

_TEMP_DATA_DIR = tempfile.mkdtemp()
_BROWN_ZIP_PATH = os.path.join(_TEMP_DATA_DIR, "brown.zip")


def download_and_extract_brown():
    if os.path.exists(_BROWN_ZIP_PATH):
        return
    try:
        _download_file(_REMOTE_BROWN_URL, _BROWN_ZIP_PATH)
    except Exception as e:
        msg = (
            f"Error '{e}' in downloading {_REMOTE_BROWN_URL}: network problems or "
            f"invalid URL for Brown zip? If URL needs updating, tutorial.rst in docs "
            "has to be updated as well."
        )
        try:
            raise e
        finally:
            pytest.exit(msg)
    else:
        with zipfile.ZipFile(_BROWN_ZIP_PATH) as zip_file:
            zip_file.extractall(path=_TEMP_DATA_DIR)


@pytest.fixture(scope="module")
def tempdir():
    download_and_extract_brown()
    cwd = os.getcwd()
    try:
        os.chdir(_TEMP_DATA_DIR)
        yield _TEMP_DATA_DIR
    finally:
        os.chdir(cwd)


pytest_collect_file = Sybil(
    parsers=[DocTestParser(ELLIPSIS | NORMALIZE_WHITESPACE), skip],
    pattern="*.rst",
    fixtures=["tempdir"],
).pytest()
