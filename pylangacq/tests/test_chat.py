from __future__ import print_function

import zipfile

import requests


BROWN_URL = 'https://childes.talkbank.org/data/Eng-NA/Brown.zip'
BROWN_ZIP_PATH = 'brown.zip'


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
    """Verify Brown zip is available for downeload and can be unzipped."""
    download_brown_zip(BROWN_ZIP_PATH)
    with zipfile.ZipFile(BROWN_ZIP_PATH) as brown_zip:
        brown_zip.extractall()

# NOTE: No new tests above this line
# pytest runs tests by the order they are defined, and so
# test_brown_zip_is_available() must run first to download the Brown zip file.
