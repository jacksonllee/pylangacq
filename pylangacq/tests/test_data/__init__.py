import os
import tempfile
import zipfile

import pytest

from pylangacq.chat import _download_file


REMOTE_BROWN_URL = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"

TEMP_DATA_DIR = tempfile.mkdtemp()
_BROWN_ZIP_PATH = os.path.join(TEMP_DATA_DIR, "brown.zip")

LOCAL_EVE_PATH = os.path.join(os.path.dirname(__file__), "eve.cha")
REMOTE_EVE_DIR = os.path.join(TEMP_DATA_DIR, "Brown", "Eve")
REMOTE_EVE_FILE_PATH = os.path.join(REMOTE_EVE_DIR, "010600a.cha")


def download_and_extract_brown():
    if os.path.exists(_BROWN_ZIP_PATH):
        return
    try:
        _download_file(REMOTE_BROWN_URL, _BROWN_ZIP_PATH)
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
