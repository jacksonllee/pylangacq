import pytest

from pylangacq.chat import Gra, ReaderNew, Utterance, Word
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


def test_utterances(eve):
    assert eve.utterances()[:2] == [
        Utterance(
            participant="CHI",
            words=[
                Word(
                    form="more",
                    pos="qn",
                    mor="more",
                    gra=Gra(source=1, target=2, rel="QUANT"),
                ),
                Word(
                    form="cookie",
                    pos="n",
                    mor="cookie",
                    gra=Gra(source=2, target=0, rel="INCROOT"),
                ),
                Word(
                    form=".", pos=".", mor="", gra=Gra(source=3, target=2, rel="PUNCT")
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
            words=[
                Word(
                    form="you",
                    pos="pro:per",
                    mor="you",
                    gra=Gra(source=1, target=2, rel="SUBJ"),
                ),
                Word(
                    form="0v",
                    pos="0v",
                    mor="v",
                    gra=Gra(source=2, target=0, rel="ROOT"),
                ),
                Word(
                    form="more",
                    pos="qn",
                    mor="more",
                    gra=Gra(source=3, target=4, rel="QUANT"),
                ),
                Word(
                    form="cookies",
                    pos="n",
                    mor="cookie-PL",
                    gra=Gra(source=4, target=2, rel="OBJ"),
                ),
                Word(
                    form="?", pos="?", mor="", gra=Gra(source=5, target=2, rel="PUNCT")
                ),
            ],
            tiers={
                "MOT": "you 0v more cookies ?",
                "%mor": "pro:per|you 0v|v qn|more n|cookie-PL ?",
                "%gra": "1|2|SUBJ 2|0|ROOT 3|4|QUANT 4|2|OBJ 5|2|PUNCT",
            },
        ),
    ]


def test_n_files(eve):
    assert eve.n_files() == 1


def test_participants(eve):
    assert eve.participants() == {"CHI", "MOT", "COL", "RIC"}


def test_languages(eve):
    assert eve.languages() == {"eng"}


def test_tagged_sents(eve):
    assert eve.tagged_sents()[0] == [
        Word(
            form="more", pos="qn", mor="more", gra=Gra(source=1, target=2, rel="QUANT")
        ),
        Word(
            form="cookie",
            pos="n",
            mor="cookie",
            gra=Gra(source=2, target=0, rel="INCROOT"),
        ),
        Word(form=".", pos=".", mor="", gra=Gra(source=3, target=2, rel="PUNCT")),
    ]


def test_tagged_words(eve):
    assert eve.tagged_words()[:5] == [
        Word(
            form="more", pos="qn", mor="more", gra=Gra(source=1, target=2, rel="QUANT")
        ),
        Word(
            form="cookie",
            pos="n",
            mor="cookie",
            gra=Gra(source=2, target=0, rel="INCROOT"),
        ),
        Word(form=".", pos=".", mor="", gra=Gra(source=3, target=2, rel="PUNCT")),
        Word(
            form="you",
            pos="pro:per",
            mor="you",
            gra=Gra(source=1, target=2, rel="SUBJ"),
        ),
        Word(form="0v", pos="0v", mor="v", gra=Gra(source=2, target=0, rel="ROOT")),
    ]


def test_sents(eve):
    assert eve.sents()[:2] == [
        ["more", "cookie", "."],
        ["you", "0v", "more", "cookies", "?"],
    ]


def test_words(eve):
    assert eve.words()[:5] == ["more", "cookie", ".", "you", "0v"]
