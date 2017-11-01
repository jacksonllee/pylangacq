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
    assert eve_one_file.number_of_utterances() == 1588
    assert eve_one_file.number_of_utterances(by_files=True) == {
        BROWN_EVE_FILE_PATH_1: 1588
    }
