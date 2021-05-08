import copy
import datetime
import filecmp
import functools
import unittest

import pytest

from pylangacq.chat import _clean_word, Reader
from pylangacq.objects import Gra, Utterance, Token
from pylangacq.tests.test_data import (
    LOCAL_EVE_PATH,
    REMOTE_BROWN_URL,
    REMOTE_EVE_DIR,
    REMOTE_EVE_FILE_PATH,
    download_and_extract_brown,
)


download_and_extract_brown()


class BaseTestCHATReader:
    """A base test class that collects all tests for a CHAT reader class.

    The intention is to allow running the same set of tests using either
    ``pylangacq.Reader`` or its subclass.
    The reader class being used is set by overriding the ``reader_class`` attribute.
    """

    # Must be set by a subclass.
    reader_class = None

    @property
    @functools.lru_cache(maxsize=1)
    def eve_local(self):
        return self.reader_class.from_files([LOCAL_EVE_PATH])

    @property
    @functools.lru_cache(maxsize=1)
    def eve_remote(self):
        return self.reader_class.from_files([REMOTE_EVE_FILE_PATH])

    def test_from_strs_same_as_from_files(self):
        with open(LOCAL_EVE_PATH, encoding="utf-8") as f:
            from_strs = self.reader_class.from_strs([f.read()])
        file_from_strs = from_strs._files[0]
        file_from_files = self.eve_local._files[0]
        assert file_from_strs.utterances == file_from_files.utterances
        assert file_from_strs.header == file_from_files.header

    def test_from_zip_remote_url(self):
        sarah_path = "Brown/Sarah/020305.cha"
        eve_path = "Brown/Eve/010600a.cha"

        r = self.reader_class.from_zip(REMOTE_BROWN_URL)
        assert r.n_files() == 214
        assert sarah_path in r.file_paths()
        assert eve_path in r.file_paths()

        r = self.reader_class.from_zip(REMOTE_BROWN_URL, "Eve")
        assert r.n_files() == 20
        assert sarah_path not in r.file_paths()
        assert eve_path in r.file_paths()

    def test_from_dir(self):
        r = self.reader_class.from_dir(REMOTE_EVE_DIR)
        assert r.n_files() == 20

    def test_clear(self):
        eve_copy = copy.deepcopy(self.eve_local)
        eve_copy.clear()
        assert eve_copy.n_files() == 0

    def test_append_and_append_left(self):
        eve_copy = copy.deepcopy(self.eve_local)
        eve_copy.append(self.eve_remote)
        assert eve_copy.file_paths() == [LOCAL_EVE_PATH, REMOTE_EVE_FILE_PATH]
        eve_copy.append_left(self.eve_remote)
        assert eve_copy.file_paths() == [
            REMOTE_EVE_FILE_PATH,
            LOCAL_EVE_PATH,
            REMOTE_EVE_FILE_PATH,
        ]

    def test_extend_and_extend_left(self):
        eve_copy = copy.deepcopy(self.eve_local)
        eve_copy.extend([self.eve_remote])
        assert eve_copy.file_paths() == [LOCAL_EVE_PATH, REMOTE_EVE_FILE_PATH]
        eve_copy.extend_left([self.eve_remote])
        assert eve_copy.file_paths() == [
            REMOTE_EVE_FILE_PATH,
            LOCAL_EVE_PATH,
            REMOTE_EVE_FILE_PATH,
        ]

    def test_pop_and_pop_left(self):
        eve = self.reader_class.from_dir(REMOTE_EVE_DIR)
        eve_path_last = eve.file_paths()[-1]
        eve_path_first = eve.file_paths()[0]

        eve_last = eve.pop()
        assert eve_last.file_paths() == [eve_path_last]
        assert eve.file_paths()[-1] != eve_path_last

        eve_first = eve.pop_left()
        assert eve_first.file_paths() == [eve_path_first]
        assert eve.file_paths()[0] != eve_path_first

    def test_utterances(self):
        assert self.eve_local.utterances()[:2] == [
            Utterance(
                participant="CHI",
                tokens=[
                    Token(
                        word="more",
                        pos="qn",
                        mor="more",
                        gra=Gra(dep=1, head=2, rel="QUANT"),
                    ),
                    Token(
                        word="cookie",
                        pos="n",
                        mor="cookie",
                        gra=Gra(dep=2, head=0, rel="INCROOT"),
                    ),
                    Token(
                        word=".", pos=".", mor="", gra=Gra(dep=3, head=2, rel="PUNCT")
                    ),
                ],
                time_marks=None,
                tiers={
                    "CHI": "more cookie . [+ IMP]",
                    "%mor": "qn|more n|cookie .",
                    "%gra": "1|2|QUANT 2|0|INCROOT 3|2|PUNCT",
                    "%int": "distinctive , loud",
                },
            ),
            Utterance(
                participant="MOT",
                tokens=[
                    Token(
                        word="you",
                        pos="pro:per",
                        mor="you",
                        gra=Gra(dep=1, head=2, rel="SUBJ"),
                    ),
                    Token(
                        word="0v",
                        pos="0v",
                        mor="v",
                        gra=Gra(dep=2, head=0, rel="ROOT"),
                    ),
                    Token(
                        word="more",
                        pos="qn",
                        mor="more",
                        gra=Gra(dep=3, head=4, rel="QUANT"),
                    ),
                    Token(
                        word="cookies",
                        pos="n",
                        mor="cookie-PL",
                        gra=Gra(dep=4, head=2, rel="OBJ"),
                    ),
                    Token(
                        word="?", pos="?", mor="", gra=Gra(dep=5, head=2, rel="PUNCT")
                    ),
                ],
                time_marks=None,
                tiers={
                    "MOT": "you 0v more cookies ?",
                    "%mor": "pro:per|you 0v|v qn|more n|cookie-PL ?",
                    "%gra": "1|2|SUBJ 2|0|ROOT 3|4|QUANT 4|2|OBJ 5|2|PUNCT",
                },
            ),
        ]

    def test_headers(self):
        assert self.eve_local.headers() == [
            {
                "Date": {datetime.date(1962, 10, 15), datetime.date(1962, 10, 17)},
                "Participants": {
                    "CHI": {
                        "name": "Eve",
                        "language": "eng",
                        "corpus": "Brown",
                        "age": "1;06.00",
                        "sex": "female",
                        "group": "",
                        "ses": "",
                        "role": "Target_Child",
                        "education": "",
                        "custom": "",
                    },
                    "MOT": {
                        "name": "Sue",
                        "language": "eng",
                        "corpus": "Brown",
                        "age": "",
                        "sex": "female",
                        "group": "",
                        "ses": "",
                        "role": "Mother",
                        "education": "",
                        "custom": "",
                    },
                    "COL": {
                        "name": "Colin",
                        "language": "eng",
                        "corpus": "Brown",
                        "age": "",
                        "sex": "",
                        "group": "",
                        "ses": "",
                        "role": "Investigator",
                        "education": "",
                        "custom": "",
                    },
                    "RIC": {
                        "name": "Richard",
                        "language": "eng",
                        "corpus": "Brown",
                        "age": "",
                        "sex": "",
                        "group": "",
                        "ses": "",
                        "role": "Investigator",
                        "education": "",
                        "custom": "",
                    },
                },
                "UTF8": "",
                "PID": "11312/c-00034743-1",
                "Languages": ["eng"],
                "Time Duration": "11:30-12:00",
                "Types": "long, toyplay, TD",
                "Tape Location": "850",
            }
        ]

    def test_n_files(self):
        assert self.eve_local.n_files() == 1

    def test_participants(self):
        assert self.eve_local.participants() == {"CHI", "MOT", "COL", "RIC"}

    def test_languages(self):
        assert self.eve_local.languages() == {"eng"}

    def test_dates_of_recording(self):
        assert self.eve_local.dates_of_recording() == {
            datetime.date(1962, 10, 15),
            datetime.date(1962, 10, 17),
        }

    def test_ages(self):
        assert self.eve_local.ages() == [(1, 6, 0)]
        assert self.eve_local.ages(months=True) == [18.0]

    def test_tokens_by_utterances(self):
        assert self.eve_local.tokens(by_utterances=True)[0] == [
            Token(
                word="more", pos="qn", mor="more", gra=Gra(dep=1, head=2, rel="QUANT")
            ),
            Token(
                word="cookie",
                pos="n",
                mor="cookie",
                gra=Gra(dep=2, head=0, rel="INCROOT"),
            ),
            Token(word=".", pos=".", mor="", gra=Gra(dep=3, head=2, rel="PUNCT")),
        ]

    def test_tokens(self):
        assert self.eve_local.tokens()[:5] == [
            Token(
                word="more", pos="qn", mor="more", gra=Gra(dep=1, head=2, rel="QUANT")
            ),
            Token(
                word="cookie",
                pos="n",
                mor="cookie",
                gra=Gra(dep=2, head=0, rel="INCROOT"),
            ),
            Token(word=".", pos=".", mor="", gra=Gra(dep=3, head=2, rel="PUNCT")),
            Token(
                word="you",
                pos="pro:per",
                mor="you",
                gra=Gra(dep=1, head=2, rel="SUBJ"),
            ),
            Token(word="0v", pos="0v", mor="v", gra=Gra(dep=2, head=0, rel="ROOT")),
        ]

    def test_words_by_utterances(self):
        assert self.eve_local.words(by_utterances=True)[:2] == [
            ["more", "cookie", "."],
            ["you", "0v", "more", "cookies", "?"],
        ]

    def test_words(self):
        assert self.eve_local.words()[:5] == ["more", "cookie", ".", "you", "0v"]

    def test_mlum(self):
        assert pytest.approx(self.eve_local.mlum(), abs=0.1) == [2.267022696929239]

    def test_mlu(self):
        assert pytest.approx(self.eve_local.mlu(), abs=0.1) == [2.267022696929239]

    def test_mluw(self):
        assert pytest.approx(self.eve_local.mluw(), abs=0.1) == [1.4459279038718291]

    def test_ttr(self):
        assert pytest.approx(self.eve_local.ttr(), abs=0.01) == [0.17543859649122806]

    def test_ipsyn(self):
        assert self.eve_local.ipsyn() == [29]

    def test_word_ngrams(self):
        assert self.eve_local.word_ngrams(1).most_common(5) == [
            ((".",), 1121),
            (("?",), 455),
            (("you",), 197),
            (("that",), 151),
            (("the",), 132),
        ]
        assert self.eve_local.word_ngrams(2).most_common(5) == [
            (("that", "?"), 101),
            (("it", "."), 63),
            (("what", "?"), 54),
            (("yes", "‡"), 45),
            (("it", "?"), 39),
        ]

    def test_word_frequency(self):
        assert self.eve_local.word_frequencies().most_common(5) == [
            (".", 1121),
            ("?", 455),
            ("you", 197),
            ("that", 151),
            ("the", 132),
        ]


class TestPylangacqReader(BaseTestCHATReader, unittest.TestCase):
    """Run the reader tests using ``pylangacq.Reader``."""

    reader_class = Reader


def test_if_childes_has_updated_data():
    assert filecmp.cmp(LOCAL_EVE_PATH, REMOTE_EVE_FILE_PATH)


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
