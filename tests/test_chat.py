import filecmp
import os
import unittest

import pytest

from pylangacq.chat import _clean_word, Reader
from pylangacq.tests.test_chat import (
    BaseTestCHATReader,
    _LOCAL_EVE_PATH,
    _REMOTE_EVE_FILE_PATH,
)


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
