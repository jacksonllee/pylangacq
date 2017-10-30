import os
import zipfile

import pytest
import requests

from pylangacq import read_chat


BROWN_URL = 'https://childes.talkbank.org/data/Eng-NA/Brown.zip'
BROWN_ZIP_PATH = 'brown.zip'


def download_file(file_path):
    try:
        with open(file_path, 'wb') as f:
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


@pytest.fixture(scope='module')
def brown_zip_path():
    """Make sure Brown zip is available for download and can be unzipped."""
    zip_path = BROWN_ZIP_PATH
    download_file(zip_path)
    return zip_path


@pytest.fixture(scope='module')
def eve(brown_zip_path):
    with zipfile.ZipFile(brown_zip_path) as zip_file:
        zip_file.extractall()
    eve_data_path = os.path.join('Brown', 'Eve', '*.cha')
    return read_chat(eve_data_path, encoding='utf-8')


def test_number_of_files(eve):
    assert len(eve) == eve.number_of_files() == 20
