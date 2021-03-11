import os
import tempfile
import zipfile

import pytest
import requests


REMOTE_BROWN_URL = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"

TEMP_DATA_DIR = tempfile.mkdtemp()
_BROWN_ZIP_PATH = os.path.join(TEMP_DATA_DIR, "brown.zip")

_THIS_DIR = os.path.dirname(__file__)
LOCAL_EVE_PATH = os.path.join(_THIS_DIR, "eve.cha")
REMOTE_EVE_DIR = os.path.join(TEMP_DATA_DIR, "Brown", "Eve")
REMOTE_EVE_FILE_PATH_1 = os.path.join(REMOTE_EVE_DIR, "010600a.cha")
REMOTE_EVE_FILE_PATH_2 = os.path.join(REMOTE_EVE_DIR, "010600b.cha")
REMOTE_EVE_FILE_PATH_ALL_FILES = os.path.join(REMOTE_EVE_DIR, "*.cha")


def download_and_extract_brown():
    if os.path.exists(_BROWN_ZIP_PATH):
        return
    try:
        with open(_BROWN_ZIP_PATH, "wb") as f:
            with requests.get(REMOTE_BROWN_URL, timeout=10) as r:
                f.write(r.content)
    except Exception as e:
        msg = (
            f"Error '{e}' in downloading {REMOTE_BROWN_URL}: network problems or "
            f"invalid URL for Brown zip? If URL needs updating, tutorial.rst in docs "
            "has to be updated as well."
        )
        try:
            raise e
        finally:
            pytest.exit(msg)
    else:
        with zipfile.ZipFile(_BROWN_ZIP_PATH) as zip_file:
            zip_file.extractall(path=TEMP_DATA_DIR)
