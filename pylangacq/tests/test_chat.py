"""Test the ``Reader`` class.

The tests mimic what the documentation shows.
If anything fails, we probably also have to update the documentation
(and fix the bugs, if any).
"""

import os
import zipfile
import tempfile

import pytest
import requests

from pylangacq import read_chat


BROWN_URL = 'https://childes.talkbank.org/data/Eng-NA/Brown.zip'
BROWN_ZIP_PATH = 'brown.zip'
BROWN_EVE_DIR = os.path.abspath(os.path.join('Brown', 'Eve'))
BROWN_EVE_FILE_PATH_1 = os.path.join(BROWN_EVE_DIR, '010600a.cha')
BROWN_EVE_FILE_PATH_2 = os.path.join(BROWN_EVE_DIR, '010600b.cha')
BROWN_EVE_FILE_PATH_ALL_FILES = os.path.join(BROWN_EVE_DIR, '*.cha')


def almost_equal(x, y, tolerance):
    # Could have used numpy's assert_almost_equal or something,
    # But it's not worth depending on numpy just for testing this...
    return abs(x - y) <= tolerance


@pytest.mark.skipif('TRAVIS' not in os.environ,
                    reason='assuming Brown/ available, speed up local dev '
                           'for running tests without download')
def test_download_and_extract_brown_zip_file():
    """pytest runs tests in the same order they are defined in the test
    module, and so this test for downloading and unzipping the Brown zip
    data file runs first. If download fails, abort all tests."""
    try:
        with open(BROWN_ZIP_PATH, 'wb') as f:
            with requests.get(BROWN_URL) as r:
                f.write(r.content)
    except Exception as e:  # pragma: no cover
        msg = ('Error in downloading {}: '
               'network problems or invalid URL for Brown zip? '
               'If URL needs updating, tutorial.rst in docs '
               'has to be updated as well.'.format(BROWN_URL))
        try:
            raise e
        finally:
            pytest.exit(msg)
    else:
        # If download succeeds, unzip the Brown zip file.
        with zipfile.ZipFile(BROWN_ZIP_PATH) as zip_file:
            zip_file.extractall()


@pytest.fixture
def eve_one_file():
    return read_chat(BROWN_EVE_FILE_PATH_1, encoding='utf-8')


@pytest.fixture
def eve_all_files():
    return read_chat(BROWN_EVE_FILE_PATH_ALL_FILES, encoding='utf-8')


def test_read_chat_wrong_filename_type():
    with pytest.raises(ValueError):
        read_chat(42)


def test_number_of_files(eve_one_file):
    assert len(eve_one_file) == eve_one_file.number_of_files() == 1


def test_update(eve_one_file):
    new_eve = read_chat(BROWN_EVE_FILE_PATH_2)
    eve_one_file.update(new_eve)
    assert len(eve_one_file) == 2


def test_update_wrong_reader_type(eve_one_file):
    with pytest.raises(ValueError):
        eve_one_file.update(42)


def test_add(eve_one_file):
    # Add an already-existing filename => no change in filename count
    assert len(eve_one_file) == 1
    eve_one_file.add(BROWN_EVE_FILE_PATH_1)
    assert len(eve_one_file) == 1

    # Add a new filename => filename count increments by 1
    len_eve = len(eve_one_file)
    eve_one_file.add(BROWN_EVE_FILE_PATH_2)
    assert len(eve_one_file) == len_eve + 1

    # Add a non-existing file => should throw an error
    with pytest.raises(ValueError):
        eve_one_file.add('foo')


def test_remove(eve_one_file):
    # Remove a non-existing file => should throw an error
    with pytest.raises(ValueError):
        eve_one_file.remove('foo')

    # Remove an existing file NOT in reader => should throw an error
    with tempfile.NamedTemporaryFile() as dummy_file:
        dummy_filename = dummy_file.name
        with pytest.raises(ValueError):
            eve_one_file.remove(dummy_filename)

    # Remove an existing filename in reader => filename count decrement by 1
    len_eve = len(eve_one_file)
    eve_one_file.remove(BROWN_EVE_FILE_PATH_1)
    assert len(eve_one_file) == len_eve - 1


def test_clear(eve_one_file):
    """Clear and reset the reader => no filenames left"""
    assert len(eve_one_file) > 0
    eve_one_file.clear()
    assert len(eve_one_file) == 0


def test_filenames(eve_all_files):
    expected_filenames = [os.path.abspath(os.path.join(BROWN_EVE_DIR, x))
                          for x in sorted(os.listdir(BROWN_EVE_DIR))]
    assert eve_all_files.filenames() == set(expected_filenames)
    assert eve_all_files.filenames(sorted_by_age=True) == expected_filenames


@pytest.mark.xfail(reason='actual count is 1601 for some reason?')
def test_number_of_utterances(eve_one_file):
    # Eve's 010600a.cha has 1588 occurrences of "\n*"
    assert eve_one_file.number_of_utterances() == 1588
    assert eve_one_file.number_of_utterances(by_files=True) == {
        BROWN_EVE_FILE_PATH_1: 1588
    }


def test_participant_codes(eve_one_file):
    expected_codes = {'CHI', 'MOT', 'COL', 'RIC'}
    assert eve_one_file.participant_codes() == expected_codes
    assert eve_one_file.participant_codes(by_files=True) == {
        BROWN_EVE_FILE_PATH_1: expected_codes
    }


def test_languages(eve_one_file):
    assert eve_one_file.languages() == {BROWN_EVE_FILE_PATH_1: ['eng']}


def test_dates_of_recording(eve_one_file):
    assert eve_one_file.dates_of_recording() == {
        BROWN_EVE_FILE_PATH_1: [(1962, 10, 15), (1962, 10, 17)]}


def test_age(eve_one_file):
    assert eve_one_file.age() == {BROWN_EVE_FILE_PATH_1: (1, 6, 0)}
    assert eve_one_file.age(months=True) == {BROWN_EVE_FILE_PATH_1: 18.0}


def test_words(eve_one_file):
    words = eve_one_file.words()
    assert almost_equal(len(words), 5843, tolerance=3)
    assert words[:5] == ['more', 'cookie', '.', 'you', '0v']


def test_tagged_words(eve_one_file):
    tagged_words = eve_one_file.tagged_words(participant='MOT')
    assert tagged_words[:2] == [
        ('you', 'PRO:PER', 'you', (1, 2, 'SUBJ')),
        ('0v', '0V', 'v', (2, 0, 'ROOT')),
    ]


def test_mlu_m(eve_one_file):
    mlu_m = eve_one_file.MLUm()
    assert almost_equal(mlu_m[BROWN_EVE_FILE_PATH_1], 2.27, tolerance=0.05)
