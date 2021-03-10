import datetime

import pytest

from pylangacq.chat import Gra, ReaderNew, Utterance, Token
from pylangacq.tests.test_data import LOCAL_EVE_PATH


_EVE = ReaderNew.from_files([LOCAL_EVE_PATH])


def test_from_strs_same_as_from_files():
    with open(LOCAL_EVE_PATH, encoding="utf8") as f:
        from_strs = ReaderNew.from_strs([f.read()])
    sr_from_strs = from_strs._single_readers[0]
    sr_from_files = _EVE._single_readers[0]
    assert sr_from_strs.utterances == sr_from_files.utterances
    assert sr_from_strs.header == sr_from_files.header


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
    assert _EVE.n_files() == 1


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


def test_tagged_sents():
    assert _EVE.tagged_sents()[0] == [
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


def test_tagged_words():
    assert _EVE.tagged_words()[:5] == [
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


def test_sents():
    assert _EVE.sents()[:2] == [
        ["more", "cookie", "."],
        ["you", "0v", "more", "cookies", "?"],
    ]


def test_words():
    assert _EVE.words()[:5] == ["more", "cookie", ".", "you", "0v"]


def test_mlum():
    assert pytest.approx(_EVE.mlum(), abs=0.1) == [3.656464709556527]


def test_mluw():
    assert pytest.approx(_EVE.mluw(), abs=0.1) == [2.5771392879450343]


def test_ttr():
    assert pytest.approx(_EVE.ttr(), abs=0.01) == [0.07192953841135215]


def test_ipsyn():
    assert _EVE.ipsyn() == [25]


def test_word_ngrams():
    assert _EVE.word_ngrams(1).most_common(5) == [
        ((".",), 1134),
        (("?",), 455),
        (("CLITIC",), 291),
        (("you",), 197),
        (("that",), 151),
    ]
    assert _EVE.word_ngrams(2).most_common(5) == [
        (("that", "?"), 101),
        (("that's", "CLITIC"), 80),
        (("it", "."), 65),
        (("what", "?"), 54),
        (("yes", "‡"), 45),
    ]


def test_word_frequency():
    assert _EVE.word_frequency().most_common(5) == [
        ((".",), 1134),
        (("?",), 455),
        (("CLITIC",), 291),
        (("you",), 197),
        (("that",), 151),
    ]
