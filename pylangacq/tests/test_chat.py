import os
import zipfile

import pytest
import requests

from pylangacq import read_chat


BROWN_URL = 'https://childes.talkbank.org/data/Eng-NA/Brown.zip'
BROWN_ZIP_PATH = 'brown.zip'


def test_download_and_extract_brown_zip_file():
    """pytest runs tests in the same order they are defined in the test
    module, and so this test for downloading and unzipping the Brown zip
    data file runs first. If download fails, abort all tests."""
    try:
        with open(BROWN_ZIP_PATH, 'wb') as f:
            with requests.get(BROWN_URL) as r:
                f.write(r.content)
    except Exception as e:  # pragma: no cover
        msg = ('Error in downloading {}: '
               'network problems or invalid URL for Brown zip? '
               'If URL needs updating, tutorial.rst in docs '
               'has to be updated as well.'.format(BROWN_URL))
        try:
            raise e
        finally:
            pytest.exit(msg)
    else:
        # If download succeeds, unzip the Brown zip file.
        with zipfile.ZipFile(BROWN_ZIP_PATH) as zip_file:
            zip_file.extractall()


@pytest.fixture
def eve():
    eve_data_path = os.path.join('Brown', 'Eve', '010600a.cha')
    return read_chat(eve_data_path, encoding='utf-8')


def test_read_chat_wrong_filename_type():
    with pytest.raises(ValueError):
        read_chat(42)


def test_number_of_files(eve):
    assert len(eve) == eve.number_of_files() == 1


def test_update(eve):
    new_eve = read_chat(os.path.join('Brown', 'Eve', '010600b.cha'))
    eve.update(new_eve)
    assert len(eve) == eve.number_of_files() == 2


def test_update_wrong_reader_type(eve):
    with pytest.raises(ValueError):
        eve.update(42)
