import filecmp
import os
import unittest
import zipfile

import pytest

from pylangacq.chat import (
    _clean_word,
    Reader,
    _download_file,
)
from pylangacq.tests.test_chat import (
    BaseTestCHATReader,
    _LOCAL_EVE_PATH,
    _REMOTE_BROWN_URL,
    _REMOTE_EVE_FILE_PATH,
    _TEMP_DATA_DIR,
)


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


download_and_extract_brown()


class TestPylangacqReader(BaseTestCHATReader, unittest.TestCase):
    """Run the reader tests using ``pylangacq.Reader``."""

    reader_class = Reader


@pytest.mark.skipif(
    os.name == "nt",
    reason="Not sure? We're good so long as this test passes on Linux and MacOS",
)
def test_if_childes_has_updated_data():
    assert filecmp.cmp(_LOCAL_EVE_PATH, _REMOTE_EVE_FILE_PATH)


@pytest.mark.parametrize(
    "original, expected",
    [
        ("foo", "foo"),
        ("&foo", "foo"),
        ("foo@bar", "foo"),
        ("foo(", "foo"),
        ("foo)", "foo"),
        ("foo:", "foo"),
        ("foo;", "foo"),
        ("foo+", "foo"),
    ],
)
def test__clean_word(original, expected):
    assert _clean_word(original) == expected
