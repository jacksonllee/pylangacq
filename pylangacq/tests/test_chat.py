import copy
import datetime
import filecmp

import pytest

from pylangacq.chat import (
    _clean_utterance,
    _clean_word,
    _remove_extra_spaces,
    _find_indices,
    Reader,
)
from pylangacq.objects import Gra, Utterance, Token
from pylangacq.tests.test_data import (
    LOCAL_EVE_PATH,
    REMOTE_BROWN_URL,
    REMOTE_EVE_DIR,
    REMOTE_EVE_FILE_PATH,
    download_and_extract_brown,
)


_EVE = Reader.from_files([LOCAL_EVE_PATH])

# This module depends on downloaded data.
download_and_extract_brown()


def test_if_childes_has_updated_data():
    assert filecmp.cmp(LOCAL_EVE_PATH, REMOTE_EVE_FILE_PATH)


def test_from_strs_same_as_from_files():
    with open(LOCAL_EVE_PATH, encoding="utf-8") as f:
        from_strs = Reader.from_strs([f.read()])
    file_from_strs = from_strs._files[0]
    file_from_files = _EVE._files[0]
    assert file_from_strs.utterances == file_from_files.utterances
    assert file_from_strs.header == file_from_files.header


def test_from_zip_remote_url():
    sarah_path = "Brown/Sarah/020305.cha"
    eve_path = "Brown/Eve/010600a.cha"

    r = Reader.from_zip(REMOTE_BROWN_URL)
    assert len(r) == 214
    assert sarah_path in r.file_paths()
    assert eve_path in r.file_paths()

    r = Reader.from_zip(REMOTE_BROWN_URL, "Eve")
    assert len(r) == 20
    assert sarah_path not in r.file_paths()
    assert eve_path in r.file_paths()


def test_from_dir():
    download_and_extract_brown()
    r = Reader.from_dir(REMOTE_EVE_DIR)
    assert len(r) == 20


def test_clear():
    eve_copy = copy.deepcopy(_EVE)
    eve_copy.clear()
    assert len(eve_copy) == 0


def test_append_remove():
    eve_copy = copy.deepcopy(_EVE)
    eve_copy.append(_EVE, ignore_repeats=False)
    assert len(eve_copy) == 2
    eve_copy.remove("eve")
    assert len(eve_copy) == 0


def test_n_utterances():
    assert _EVE.n_utterances() == 1601


def test_utterances():
    assert _EVE.utterances()[:2] == [
        Utterance(
            participant="CHI",
            tokens=[
                Token(
                    word="more",
                    pos="qn",
                    mor="more",
                    gra=Gra(source=1, target=2, rel="QUANT"),
                ),
                Token(
                    word="cookie",
                    pos="n",
                    mor="cookie",
                    gra=Gra(source=2, target=0, rel="INCROOT"),
                ),
                Token(
                    word=".", pos=".", mor="", gra=Gra(source=3, target=2, rel="PUNCT")
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
                    gra=Gra(source=1, target=2, rel="SUBJ"),
                ),
                Token(
                    word="0v",
                    pos="0v",
                    mor="v",
                    gra=Gra(source=2, target=0, rel="ROOT"),
                ),
                Token(
                    word="more",
                    pos="qn",
                    mor="more",
                    gra=Gra(source=3, target=4, rel="QUANT"),
                ),
                Token(
                    word="cookies",
                    pos="n",
                    mor="cookie-PL",
                    gra=Gra(source=4, target=2, rel="OBJ"),
                ),
                Token(
                    word="?", pos="?", mor="", gra=Gra(source=5, target=2, rel="PUNCT")
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


def test_headers():
    assert _EVE.headers() == [
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


def test_n_files():
    assert _EVE.n_files() == len(_EVE) == 1


def test_participants():
    assert _EVE.participants() == {"CHI", "MOT", "COL", "RIC"}


def test_languages():
    assert _EVE.languages() == {"eng"}


def test_dates_of_recording():
    assert _EVE.dates_of_recording() == {
        datetime.date(1962, 10, 15),
        datetime.date(1962, 10, 17),
    }


def test_ages():
    assert _EVE.ages() == [(1, 6, 0)]
    assert _EVE.ages(months=True) == [18.0]


def test_tokens_by_utterances():
    assert _EVE.tokens(by_utterances=True)[0] == [
        Token(
            word="more", pos="qn", mor="more", gra=Gra(source=1, target=2, rel="QUANT")
        ),
        Token(
            word="cookie",
            pos="n",
            mor="cookie",
            gra=Gra(source=2, target=0, rel="INCROOT"),
        ),
        Token(word=".", pos=".", mor="", gra=Gra(source=3, target=2, rel="PUNCT")),
    ]


def test_tokens():
    assert _EVE.tokens()[:5] == [
        Token(
            word="more", pos="qn", mor="more", gra=Gra(source=1, target=2, rel="QUANT")
        ),
        Token(
            word="cookie",
            pos="n",
            mor="cookie",
            gra=Gra(source=2, target=0, rel="INCROOT"),
        ),
        Token(word=".", pos=".", mor="", gra=Gra(source=3, target=2, rel="PUNCT")),
        Token(
            word="you",
            pos="pro:per",
            mor="you",
            gra=Gra(source=1, target=2, rel="SUBJ"),
        ),
        Token(word="0v", pos="0v", mor="v", gra=Gra(source=2, target=0, rel="ROOT")),
    ]


def test_words_by_utterances():
    assert _EVE.words(by_utterances=True)[:2] == [
        ["more", "cookie", "."],
        ["you", "0v", "more", "cookies", "?"],
    ]


def test_words():
    assert _EVE.words()[:5] == ["more", "cookie", ".", "you", "0v"]


def test_mlum():
    assert pytest.approx(_EVE.mlum(), abs=0.1) == [2.267022696929239]


def test_mlu():
    assert pytest.approx(_EVE.mlu(), abs=0.1) == [2.267022696929239]


def test_mluw():
    assert pytest.approx(_EVE.mluw(), abs=0.1) == [1.4459279038718291]


def test_ttr():
    assert pytest.approx(_EVE.ttr(), abs=0.01) == [0.17543859649122806]


def test_ipsyn():
    assert _EVE.ipsyn() == [29]


def test_word_ngrams():
    assert _EVE.word_ngrams(1).most_common(5) == [
        ((".",), 1134),
        (("?",), 455),
        (("you",), 197),
        (("that",), 151),
        (("the",), 132),
    ]
    assert _EVE.word_ngrams(2).most_common(5) == [
        (("that", "?"), 101),
        (("it", "."), 65),
        (("what", "?"), 54),
        (("yes", "‡"), 45),
        (("it", "?"), 39),
    ]


def test_word_frequency():
    assert _EVE.word_frequencies().most_common(5) == [
        (".", 1134),
        ("?", 455),
        ("you", 197),
        ("that", 151),
        ("the", 132),
    ]


@pytest.mark.parametrize(
    "original, expected",
    [
        ("[= foo ] bar", "bar"),
        ("[x 2] bar", "bar"),
        ("[+ foo ] bar", "bar"),
        ("[* foo ] bar", "bar"),
        ("[=? foo ] bar", "bar"),
        ("[=! foo ] bar", "bar"),
        ("[% foo ] bar", "bar"),
        ("[- foo ] bar", "bar"),
        ("[^ foo ] bar", "bar"),
        ("[<1] bar", "bar"),
        ("[<] bar", "bar"),
        ("[>1] bar", "bar"),
        ("[>] bar", "bar"),
        ("[<1] bar", "bar"),
        ("(1) bar", "bar"),
        ("(1.) bar", "bar"),
        ("(1.3) bar", "bar"),
        ("(1.34) bar", "bar"),
        ("(12.34) bar", "bar"),
        ("[%act: foo] bar", "bar"),
        ("[?] bar", "bar"),
        ("[!] bar", "bar"),
        ("‹ bar", "bar"),
        ("› bar", "bar"),
        ("bar", "bar"),
        ("[*] bar", "bar"),
        ("bar [*]", "bar"),
        ("“bar”", "bar"),
        # Step 3
        ("foo bar [/-]", "foo"),
        ("foo < bar baz > [/-]", "foo"),
    ],
)
def test__clean_utterance(original, expected):
    # TODO: Most of step 3 and all of step 5 in the function not tested
    assert _clean_utterance(original) == expected


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


@pytest.mark.parametrize(
    "original, expected",
    [("foo  bar", "foo bar"), ("foo bar  baz", "foo bar baz")],
)
def test__remove_extra_spaces(original, expected):
    assert _remove_extra_spaces(original) == expected


@pytest.mark.parametrize(
    "original, target, expected",
    [
        ("foo bar", "foo", [0]),
        ("foo foo bar", "foo", [0, 4]),
        ("foo bar foo", "foo", [0, 8]),
        ("foo bar baz", "bar", [4]),
    ],
)
def test__find_indices(original, target, expected):
    assert _find_indices(original, target) == expected
