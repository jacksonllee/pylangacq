import filecmp
import os
import unittest

import pytest

from pylangacq.chat import _clean_word, Reader, _CLITIC_REGEX
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


@pytest.mark.parametrize(
    "source, expected_pre, expected_core, expected_post",
    [
        ("abc", None, "abc", None),
        ("abc$def~ghi", "abc", "def", "ghi"),
        ("blah$abc$def~ghi", "blah$abc", "def", "ghi"),
        ("abc$def", "abc", "def", None),
        ("abc$def$blah", "abc$def", "blah", None),
        ("abc$def~ghi~blah", "abc", "def", "ghi~blah"),
        ("def~ghi~blah", None, "def", "ghi~blah"),
        ("blah$abc$def~ghi~blah", "blah$abc", "def", "ghi~blah"),
    ],
)
def test__clitic_regex(source, expected_pre, expected_core, expected_post):
    match = _CLITIC_REGEX.search(source)
    _, actual_pre, actual_core, _, actual_post = match.groups()
    assert actual_pre == expected_pre
    assert actual_core == expected_core
    assert actual_post == expected_post
