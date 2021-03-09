import pytest

from pylangacq.chat import ReaderNew
from pylangacq.tests.test_data import LOCAL_EVE_PATH


@pytest.fixture
def eve():
    return ReaderNew.from_files([LOCAL_EVE_PATH])


def test_from_strs_same_as_from_files(eve):
    with open(LOCAL_EVE_PATH, encoding="utf8") as f:
        from_strs = ReaderNew.from_strs([f.read()])
    sr_from_strs = from_strs._single_readers[0]
    sr_from_files = eve._single_readers[0]
    assert sr_from_strs.utterances == sr_from_files.utterances
    assert sr_from_strs.header == sr_from_files.header


def test_n_utterances(eve):
    assert eve.n_utterances() == 1601


def test_n_files(eve):
    assert eve.n_files() == 1


def test_participants(eve):
    assert eve.participants() == {"CHI", "MOT", "COL", "RIC"}


def test_languages(eve):
    assert eve.languages() == {"eng"}
