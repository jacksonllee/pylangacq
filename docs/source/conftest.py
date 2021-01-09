"""Test code snippets embedded in the docs.

Reference: https://sybil.readthedocs.io/en/latest/use.html#pytest
"""

import os
from doctest import ELLIPSIS

import pytest
from sybil import Sybil
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.skip import skip

from pylangacq.tests.test_data import download_and_extract_brown, TEMP_DATA_DIR


@pytest.fixture(scope="module")
def tempdir():
    download_and_extract_brown()
    cwd = os.getcwd()
    try:
        os.chdir(TEMP_DATA_DIR)
        yield TEMP_DATA_DIR
    finally:
        os.chdir(cwd)


pytest_collect_file = Sybil(
    parsers=[DocTestParser(optionflags=ELLIPSIS), skip],
    pattern="*.rst",
    fixtures=["tempdir"],
).pytest()
