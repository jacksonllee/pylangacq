import copy
import datetime
import functools
import os
import tempfile
import zipfile
from unittest import mock

import pytest

from pylangacq.chat import cached_data_info, remove_cached_data, _download_file
from pylangacq.objects import Gra, Utterance, Token


_REMOTE_BROWN_URL = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"

_TEMP_DATA_DIR = tempfile.mkdtemp()

_LOCAL_EVE_PATH = os.path.join(os.path.dirname(__file__), "eve.cha")
_REMOTE_EVE_DIR = os.path.join(_TEMP_DATA_DIR, "Brown", "Eve")
_REMOTE_EVE_FILE_PATH = os.path.join(_REMOTE_EVE_DIR, "010600a.cha")

_EXPECTED_EVE_UTTERANCES = [
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
            Token(word=".", pos=".", mor="", gra=Gra(dep=3, head=2, rel="PUNCT")),
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
            Token(word="?", pos="?", mor="", gra=Gra(dep=5, head=2, rel="PUNCT")),
        ],
        time_marks=None,
        tiers={
            "MOT": "you 0v more cookies ?",
            "%mor": "pro:per|you 0v|v qn|more n|cookie-PL ?",
            "%gra": "1|2|SUBJ 2|0|ROOT 3|4|QUANT 4|2|OBJ 5|2|PUNCT",
        },
    ),
]


_BROWN_ZIP_PATH = os.path.join(_TEMP_DATA_DIR, "brown.zip")


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
        return self.reader_class.from_files([_LOCAL_EVE_PATH])

    @property
    @functools.lru_cache(maxsize=1)
    def eve_remote(self):
        download_and_extract_brown()
        return self.reader_class.from_files([_REMOTE_EVE_FILE_PATH])

    def test_use_cached(self):
        remove_cached_data()
        assert len(cached_data_info()) == 0

        self.reader_class.from_zip(_REMOTE_BROWN_URL, match="Eve")
        assert len(cached_data_info()) == 1
        assert _REMOTE_BROWN_URL in cached_data_info()

        # Use a mock session to block internet access.
        # The `from_zip` shouldn't crash and shouldn't use the session object anyway,
        # because it should use the cached data.
        mock_session = mock.Mock()
        self.reader_class.from_zip(_REMOTE_BROWN_URL, match="Eve", session=mock_session)
        assert len(cached_data_info()) == 1
        assert _REMOTE_BROWN_URL in cached_data_info()
        mock_session.get.assert_not_called()

        remove_cached_data()
        assert len(cached_data_info()) == 0

    def test_from_strs_same_as_from_files(self):
        with open(_LOCAL_EVE_PATH, encoding="utf-8") as f:
            from_strs = self.reader_class.from_strs([f.read()])
        file_from_strs = from_strs._files[0]
        file_from_files = self.eve_local._files[0]
        assert file_from_strs.utterances == file_from_files.utterances
        assert file_from_strs.header == file_from_files.header

    def test_from_dir(self):
        r = self.reader_class.from_dir(_REMOTE_EVE_DIR)
        assert r.n_files() == 20

    def test_to_strs(self):
        expected = (
            "@Languages:\teng , yue\n"
            "@Participants:\tFOO Foo P1 , BAR Bar P2\n"
            "@ID:\teng|Foobar|FOO||female|||P1|||\n"
            "@ID:\teng|Foobar|BAR||male|||P2|||\n"
            "@Date:\t03-NOV-2016\n"
            "@Comment:\tThis is a comment.\n"
            "*FOO:\thow are you ?\n"
            "*BAR:\tfine , thank you ."
        )
        reader = self.reader_class.from_strs([expected])
        actual = list(reader.to_strs())[0]
        assert actual.strip() == expected.strip()

    def test_to_chat_is_dir_true(self):
        expected = (
            "@Languages:\teng , yue\n"
            "@Participants:\tFOO Foo P1 , BAR Bar P2\n"
            "@ID:\teng|Foobar|FOO||female|||P1|||\n"
            "@ID:\teng|Foobar|BAR||male|||P2|||\n"
            "@Date:\t03-NOV-2016\n"
            "@Comment:\tThis is a comment.\n"
            "*FOO:\thow are you ?\n"
            "*BAR:\tfine , thank you .\n"
        )
        reader = self.reader_class.from_strs([expected])
        with tempfile.TemporaryDirectory() as temp_dir:
            reader.to_chat(temp_dir, is_dir=True)
            assert os.listdir(temp_dir) == ["0001.cha"]
            with open(os.path.join(temp_dir, "0001.cha"), encoding="utf-8") as f:
                assert f.read() == expected

    def test_to_chat_is_dir_false(self):
        expected = (
            "@Languages:\teng , yue\n"
            "@Participants:\tFOO Foo P1 , BAR Bar P2\n"
            "@ID:\teng|Foobar|FOO||female|||P1|||\n"
            "@ID:\teng|Foobar|BAR||male|||P2|||\n"
            "@Date:\t03-NOV-2016\n"
            "@Comment:\tThis is a comment.\n"
            "*FOO:\thow are you ?\n"
            "*BAR:\tfine , thank you .\n"
        )
        reader = self.reader_class.from_strs([expected])
        with tempfile.TemporaryDirectory() as temp_dir:
            basename = "data.cha"
            file_path = os.path.join(temp_dir, basename)
            reader.to_chat(file_path)
            assert os.listdir(temp_dir) == [basename]
            with open(file_path, encoding="utf-8") as f:
                assert f.read() == expected

    def test_round_trip_to_strs_and_from_strs_for_tabular_true(self):
        original = self.eve_local
        new = self.reader_class.from_strs([list(original.to_strs(tabular=True))[0]])
        assert original.n_files() == new.n_files() == 1
        assert (
            # Utterance count
            sum(len(f.utterances) for f in original._files)
            == sum(len(f.utterances) for f in new._files)
            == 1588
        )
        assert (
            # Word count
            sum(len(u.tokens) for f in original._files for u in f.utterances)
            == sum(len(u.tokens) for f in new._files for u in f.utterances)
            == 6107
        )

    def test_clear(self):
        eve_copy = copy.deepcopy(self.eve_local)
        eve_copy.clear()
        assert eve_copy.n_files() == 0

    def test_add(self):
        reader1 = self.reader_class.from_strs(["*X: foo"])
        reader2 = self.reader_class.from_strs(["*X: bar"])
        reader3 = self.reader_class.from_strs(["*X: baz"])
        assert list((reader1 + reader2).to_strs()) == ["*X:\tfoo\n", "*X:\tbar\n"]
        reader2 += reader3
        assert list(reader2.to_strs()) == ["*X:\tbar\n", "*X:\tbaz\n"]

    def test_append_and_append_left(self):
        eve_copy = copy.deepcopy(self.eve_local)
        eve_copy.append(self.eve_remote)
        assert eve_copy.file_paths() == [_LOCAL_EVE_PATH, _REMOTE_EVE_FILE_PATH]
        eve_copy.append_left(self.eve_remote)
        assert eve_copy.file_paths() == [
            _REMOTE_EVE_FILE_PATH,
            _LOCAL_EVE_PATH,
            _REMOTE_EVE_FILE_PATH,
        ]

    def test_extend_and_extend_left(self):
        eve_copy = copy.deepcopy(self.eve_local)
        eve_copy.extend([self.eve_remote])
        assert eve_copy.file_paths() == [_LOCAL_EVE_PATH, _REMOTE_EVE_FILE_PATH]
        eve_copy.extend_left([self.eve_remote])
        assert eve_copy.file_paths() == [
            _REMOTE_EVE_FILE_PATH,
            _LOCAL_EVE_PATH,
            _REMOTE_EVE_FILE_PATH,
        ]

    def test_pop_and_pop_left(self):
        eve = self.reader_class.from_dir(_REMOTE_EVE_DIR)
        eve_path_last = eve.file_paths()[-1]
        eve_path_first = eve.file_paths()[0]

        eve_last = eve.pop()
        assert eve_last.file_paths() == [eve_path_last]
        assert eve.file_paths()[-1] != eve_path_last

        eve_first = eve.pop_left()
        assert eve_first.file_paths() == [eve_path_first]
        assert eve.file_paths()[0] != eve_path_first

    @pytest.mark.skipif(os.name == "nt", reason="Windows OS sep is backslash instead")
    def test_filter(self):
        # Just two paths for each child in the American English Brown corpus.
        eve_paths = {"Brown/Eve/010600a.cha", "Brown/Eve/010600b.cha"}
        sarah_paths = {"Brown/Sarah/020305.cha", "Brown/Sarah/020307.cha"}
        adam_paths = {"Brown/Adam/020304.cha", "Brown/Adam/020318.cha"}

        adam_and_eve = self.reader_class.from_zip(_REMOTE_BROWN_URL, exclude="Sarah")

        assert eve_paths.issubset(set(adam_and_eve.file_paths()))
        assert not sarah_paths.issubset(set(adam_and_eve.file_paths()))
        assert adam_paths.issubset(set(adam_and_eve.file_paths()))

        adam = adam_and_eve.filter(exclude="Eve")
        assert not eve_paths.issubset(set(adam.file_paths()))
        assert adam_paths.issubset(set(adam.file_paths()))

        eve = adam_and_eve.filter(match="Eve")
        assert eve_paths.issubset(set(eve.file_paths()))
        assert not adam_paths.issubset(set(eve.file_paths()))

    def test_utterances(self):
        assert self.eve_local.utterances()[:2] == _EXPECTED_EVE_UTTERANCES

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

    def test_headers_more_lenient_parsing(self):
        header1 = "@UTF8\n@Foo:\tone two\n@Foo Bar:\thello how are you"
        header2 = "@UTF8\n@Foo: one two\n@Foo Bar: hello how are you"
        reader1 = self.reader_class.from_strs([header1])
        reader2 = self.reader_class.from_strs([header2])
        expected = {"UTF8": "", "Foo": "one two", "Foo Bar": "hello how are you"}
        assert reader1.headers()[0] == reader2.headers()[0] == expected

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
            (("you",), 196),
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
            ("you", 196),
            ("that", 151),
            ("the", 132),
        ]

    def test_file_from_empty_string(self):
        # pytest.mark.parameterize didn't work for a class method?
        for empty_input in ("", None):
            reader = self.reader_class.from_strs([empty_input])
            file_ = reader._files[0]

            assert file_.header == {}
            assert file_.utterances == []

            assert reader.headers() == [{}]
            assert reader.ages() == [None]
            assert reader.dates_of_recording() == set()
            assert reader.languages() == set()
            assert reader.participants() == set()


def download_and_extract_brown():
    if os.path.exists(_BROWN_ZIP_PATH):
        return
    try:
        _download_file(_REMOTE_BROWN_URL, _BROWN_ZIP_PATH)
    except Exception as e:
        msg = (
            f"Error '{e}' in downloading {_REMOTE_BROWN_URL}: network problems or "
            f"invalid URL for Brown zip? If URL needs updating, tutorial.rst in docs "
            "has to be updated as well."
        )
        try:
            raise e
        finally:
            pytest.exit(msg)
    else:
        with zipfile.ZipFile(_BROWN_ZIP_PATH) as zip_file:
            zip_file.extractall(path=_TEMP_DATA_DIR)
