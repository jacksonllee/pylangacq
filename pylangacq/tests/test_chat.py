"""Test the ``Reader`` class.

The tests mimic what the documentation shows.
If anything fails, we probably also have to update the documentation
(and fix the bugs, if any).
"""

import filecmp
import os
import tempfile

import pytest

from pylangacq import read_chat, Reader
from pylangacq.tests.test_data import (
    LOCAL_EVE_PATH,
    REMOTE_EVE_DIR,
    REMOTE_EVE_FILE_PATH_1,
    REMOTE_EVE_FILE_PATH_2,
    REMOTE_EVE_FILE_PATH_ALL_FILES,
    download_and_extract_brown,
)

# This module depends on downloaded data.
download_and_extract_brown()


def test_if_childes_has_updated_data():
    assert filecmp.cmp(LOCAL_EVE_PATH, REMOTE_EVE_FILE_PATH_1)


@pytest.fixture
def eve_one_file():
    return read_chat(LOCAL_EVE_PATH, encoding="utf-8")


@pytest.fixture
def eve_all_files():
    return read_chat(REMOTE_EVE_FILE_PATH_ALL_FILES, encoding="utf-8")


@pytest.mark.parametrize(
    "classmethod,arg",
    [
        pytest.param(
            Reader.from_chat_str,
            open(LOCAL_EVE_PATH, encoding="utf-8").read(),
            id="from_chat_str",
        ),
        pytest.param(Reader.from_chat_files, LOCAL_EVE_PATH, id="from_chat_files"),
    ],
)
def test_instantiate_reader(classmethod, arg):
    """`read_chat` and the from_x classmethods works the same."""
    from_classmethod = classmethod(arg, encoding="utf-8")
    from_read_chat = read_chat(REMOTE_EVE_FILE_PATH_1, encoding="utf-8")

    # "header" and "index_to_tiers" combined cover the entire data file
    header_from_classmethod = list(from_classmethod.headers().values())[0]
    header_from_read_chat = list(from_read_chat.headers().values())[0]

    index_to_tiers_from_classmethod = list(from_classmethod.index_to_tiers().values())[
        0
    ]
    index_to_tiers_from_read_chat = list(from_read_chat.index_to_tiers().values())[0]

    assert header_from_classmethod == header_from_read_chat
    assert len(index_to_tiers_from_classmethod) == len(index_to_tiers_from_read_chat)

    for (i_c, tier_c), (i_r, tier_r) in zip(
        sorted(index_to_tiers_from_classmethod.items()),
        sorted(index_to_tiers_from_read_chat.items()),
    ):
        try:
            assert tier_c == tier_r
        except AssertionError:
            print("i_c:", i_c, "i_r:", i_r)
            raise


def test_read_chat_wrong_filename_type():
    with pytest.raises(ValueError):
        read_chat(42)


def test_number_of_files(eve_one_file):
    assert len(eve_one_file) == eve_one_file.number_of_files() == 1


def test_update(eve_one_file):
    new_eve = read_chat(REMOTE_EVE_FILE_PATH_2)
    eve_one_file.update(new_eve)
    assert len(eve_one_file) == 2


def test_update_wrong_reader_type(eve_one_file):
    with pytest.raises(ValueError):
        eve_one_file.update(42)


def test_add(eve_one_file):
    # Add an already-existing filename => no change in filename count
    assert len(eve_one_file) == 1
    eve_one_file.add(LOCAL_EVE_PATH)
    assert len(eve_one_file) == 1

    # Add a new filename => filename count increments by 1
    len_eve = len(eve_one_file)
    eve_one_file.add(REMOTE_EVE_FILE_PATH_2)
    assert len(eve_one_file) == len_eve + 1

    # Add a non-existing file => should throw an error
    with pytest.raises(ValueError):
        eve_one_file.add("foo")


def test_remove(eve_one_file):
    # Remove a non-existing file => should throw an error
    with pytest.raises(ValueError):
        eve_one_file.remove("foo")

    # Remove an existing file NOT in reader => should throw an error
    with tempfile.NamedTemporaryFile() as dummy_file:
        dummy_filename = dummy_file.name
        with pytest.raises(ValueError):
            eve_one_file.remove(dummy_filename)

    # Remove an existing filename in reader => filename count decrement by 1
    len_eve = len(eve_one_file)
    eve_one_file.remove(LOCAL_EVE_PATH)
    assert len(eve_one_file) == len_eve - 1


def test_clear(eve_one_file):
    """Clear and reset the reader => no filenames left"""
    assert len(eve_one_file) > 0
    eve_one_file.clear()
    assert len(eve_one_file) == 0


def test_filenames(eve_all_files):
    expected_filenames = [
        os.path.abspath(os.path.join(REMOTE_EVE_DIR, x))
        for x in sorted(os.listdir(REMOTE_EVE_DIR))
    ]
    assert eve_all_files.filenames() == set(expected_filenames)
    assert eve_all_files.filenames(sorted_by_age=True) == expected_filenames


def test_number_of_utterances(eve_one_file):
    actual1 = eve_one_file.number_of_utterances()
    actual2 = eve_one_file.number_of_utterances(by_files=True)[LOCAL_EVE_PATH]
    assert actual1 == actual2 == 1601


def test_participant_codes(eve_one_file):
    expected_codes = {"CHI", "MOT", "COL", "RIC"}
    assert eve_one_file.participant_codes() == expected_codes
    assert eve_one_file.participant_codes(by_files=True) == {
        LOCAL_EVE_PATH: expected_codes
    }


def test_languages(eve_one_file):
    assert eve_one_file.languages() == {LOCAL_EVE_PATH: ["eng"]}


def test_dates_of_recording(eve_one_file):
    assert eve_one_file.dates_of_recording() == {
        LOCAL_EVE_PATH: [(1962, 10, 15), (1962, 10, 17)]
    }


def test_age(eve_one_file):
    assert eve_one_file.age() == {LOCAL_EVE_PATH: (1, 6, 0)}
    assert eve_one_file.age(months=True) == {LOCAL_EVE_PATH: 18.0}


def test_words(eve_one_file):
    words = eve_one_file.words()
    assert len(words) == 5840
    assert words[:5] == ["more", "cookie", ".", "you", "0v"]


def test_tagged_words(eve_one_file):
    tagged_words = eve_one_file.tagged_words(participant="MOT")
    assert tagged_words[:2] == [
        ("you", "PRO:PER", "you", (1, 2, "SUBJ")),
        ("0v", "0V", "v", (2, 0, "ROOT")),
    ]


def test_word_frequency(eve_all_files):
    word_freq = eve_all_files.word_frequency()
    expected_top_five = [
        (".", 20130),
        ("?", 6358),
        ("you", 3695),
        ("the", 2524),
        ("it", 2365),
    ]
    for expected, actual in zip(expected_top_five, word_freq.most_common(5)):
        expected_word, expected_freq = expected
        actual_word, actual_freq = actual
        assert expected_word == actual_word
        assert expected_freq == actual_freq


def test_word_ngrams(eve_all_files):
    bigrams = eve_all_files.word_ngrams(2)
    expected_top_five = [
        (("it", "."), 705),
        (("that", "?"), 619),
        (("what", "?"), 560),
        (("yeah", "."), 510),
        (("there", "."), 471),
    ]
    for expected, actual in zip(expected_top_five, bigrams.most_common(5)):
        expected_bigram, expected_freq = expected
        actual_bigram, actual_freq = actual
        assert expected_bigram == actual_bigram
        assert expected_freq == actual_freq


def test_participants(eve_one_file):
    assert eve_one_file.participants()[LOCAL_EVE_PATH] == {
        "CHI": {
            "SES": "",
            "age": "1;06.00",
            "corpus": "Brown",
            "custom": "",
            "education": "",
            "group": "",
            "language": "eng",
            "participant_name": "Eve",
            "participant_role": "Target_Child",
            "sex": "female",
        },
        "COL": {
            "SES": "",
            "age": "",
            "corpus": "Brown",
            "custom": "",
            "education": "",
            "group": "",
            "language": "eng",
            "participant_name": "Colin",
            "participant_role": "Investigator",
            "sex": "",
        },
        "MOT": {
            "SES": "",
            "age": "",
            "corpus": "Brown",
            "custom": "",
            "education": "",
            "group": "",
            "language": "eng",
            "participant_name": "Sue",
            "participant_role": "Mother",
            "sex": "female",
        },
        "RIC": {
            "SES": "",
            "age": "",
            "corpus": "Brown",
            "custom": "",
            "education": "",
            "group": "",
            "language": "eng",
            "participant_name": "Richard",
            "participant_role": "Investigator",
            "sex": "",
        },
    }


def test_headers(eve_one_file):
    assert eve_one_file.headers()[LOCAL_EVE_PATH] == {
        "Date": ["15-OCT-1962", "17-OCT-1962"],
        "Languages": "eng",
        "PID": "11312/c-00034743-1",
        "Participants": {
            "CHI": {
                "SES": "",
                "age": "1;06.00",
                "corpus": "Brown",
                "custom": "",
                "education": "",
                "group": "",
                "language": "eng",
                "participant_name": "Eve",
                "participant_role": "Target_Child",
                "sex": "female",
            },
            "COL": {
                "SES": "",
                "age": "",
                "corpus": "Brown",
                "custom": "",
                "education": "",
                "group": "",
                "language": "eng",
                "participant_name": "Colin",
                "participant_role": "Investigator",
                "sex": "",
            },
            "MOT": {
                "SES": "",
                "age": "",
                "corpus": "Brown",
                "custom": "",
                "education": "",
                "group": "",
                "language": "eng",
                "participant_name": "Sue",
                "participant_role": "Mother",
                "sex": "female",
            },
            "RIC": {
                "SES": "",
                "age": "",
                "corpus": "Brown",
                "custom": "",
                "education": "",
                "group": "",
                "language": "eng",
                "participant_name": "Richard",
                "participant_role": "Investigator",
                "sex": "",
            },
        },
        "Tape Location": "850",
        "Time Duration": "11:30-12:00",
        "Types": "long, toyplay, TD",
        "UTF8": "",
    }


def test_sents(eve_one_file):
    assert eve_one_file.sents()[:2] == [
        ["more", "cookie", "."],
        ["you", "0v", "more", "cookies", "?"],
    ]


def test_tagged_sents(eve_one_file):
    assert eve_one_file.tagged_sents()[:2] == [
        [
            ("more", "QN", "more", (1, 2, "QUANT")),
            ("cookie", "N", "cookie", (2, 0, "INCROOT")),
            (".", ".", "", (3, 2, "PUNCT")),
        ],
        [
            ("you", "PRO:PER", "you", (1, 2, "SUBJ")),
            ("0v", "0V", "v", (2, 0, "ROOT")),
            ("more", "QN", "more", (3, 4, "QUANT")),
            ("cookies", "N", "cookie-PL", (4, 2, "OBJ")),
            ("?", "?", "", (5, 2, "PUNCT")),
        ],
    ]


def test_utterances(eve_one_file):
    assert eve_one_file.utterances()[:5] == [
        ("CHI", "more cookie ."),
        ("MOT", "you 0v more cookies ?"),
        ("MOT", "how_about another graham+cracker ?"),
        ("MOT", "would that do just as_well ?"),
        ("MOT", "here ."),
    ]


def test_part_of_speech_tags(eve_all_files):
    assert len(eve_all_files.part_of_speech_tags()) == 62


def test_mlu_m(eve_one_file):
    mlu_m = eve_one_file.MLUm()
    assert mlu_m[LOCAL_EVE_PATH] == pytest.approx(2.27, abs=0.01)


def test_mlu_w(eve_one_file):
    mlu_w = eve_one_file.MLUw()
    assert mlu_w[LOCAL_EVE_PATH] == pytest.approx(1.45, abs=0.01)


def test_ttr(eve_one_file):
    ttr = eve_one_file.TTR()
    assert ttr[LOCAL_EVE_PATH] == pytest.approx(0.18, abs=0.01)


def test_ipsyn(eve_one_file):
    ipsyn = eve_one_file.IPSyn()
    assert ipsyn[LOCAL_EVE_PATH] == 29
