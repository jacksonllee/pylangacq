from pylangacq.chat import ReaderNew
from pylangacq.tests.test_data import LOCAL_EVE_PATH


def test_from_files():
    ReaderNew.from_files([LOCAL_EVE_PATH])


def test_from_strs():
    with open(LOCAL_EVE_PATH, encoding="utf8") as f:
        ReaderNew.from_strs([f.read()])
