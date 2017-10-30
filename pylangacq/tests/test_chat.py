from __future__ import print_function

import zipfile
import tempfile

import requests


BROWN_URL = 'https://childes.talkbank.org/data/Eng-NA/Brown.zip'


def download_brown_zip(zip_path):
    try:
        with open(zip_path, 'wb') as brown_zip_file:
            with requests.get(BROWN_URL) as r:
                brown_zip_file.write(r.content)
    except:  # pragma: no cover  # noqa
        print('Error in downloading Brown zip: '
              'network problems or invalid URL for Brown zip?\n'
              'If URL needs updating, tutorial.rst in docs has to be updated '
              'as well\n.')
        raise


def test_brown_zip_is_available():
    """Verify Brown zip is available for download and can be unzipped."""
    with tempfile.NamedTemporaryFile() as temp_zip_file:
        zip_path = temp_zip_file.name

        download_brown_zip(zip_path)
        with zipfile.ZipFile(zip_path) as brown_zip:
            brown_zip.extractall()
