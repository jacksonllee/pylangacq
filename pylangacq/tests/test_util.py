# -*- coding: utf-8 -*-

from pylangacq.util import (clean_utterance, get_participant_code, clean_word,
                            convert_date_to_tuple, get_lemma_from_mor,
                            remove_extra_spaces, find_indices)


def test_clean_utterance():
    # TODO: Steps 3 and 4 in the function not tested
    assert clean_utterance('[= foo ] bar') == 'bar'
    assert clean_utterance('[x 2] bar') == 'bar'
    assert clean_utterance('[+ foo ] bar') == 'bar'
    assert clean_utterance('[* foo ] bar') == 'bar'
    assert clean_utterance('[=? foo ] bar') == 'bar'
    assert clean_utterance('[=! foo ] bar') == 'bar'
    assert clean_utterance('[% foo ] bar') == 'bar'
    assert clean_utterance('[- foo ] bar') == 'bar'
    assert clean_utterance('[^ foo ] bar') == 'bar'
    assert clean_utterance('[<1] bar') == 'bar'
    assert clean_utterance('[<] bar') == 'bar'
    assert clean_utterance('[>1] bar') == 'bar'
    assert clean_utterance('[>] bar') == 'bar'
    assert clean_utterance('[<1] bar') == 'bar'
    assert clean_utterance('(1) bar') == 'bar'
    assert clean_utterance('(1.) bar') == 'bar'
    assert clean_utterance('(1.3) bar') == 'bar'
    assert clean_utterance('(1.34) bar') == 'bar'
    assert clean_utterance('(12.34) bar') == 'bar'
    assert clean_utterance('[%act: foo] bar') == 'bar'
    assert clean_utterance('[?] bar') == 'bar'
    assert clean_utterance('[!] bar') == 'bar'
    assert clean_utterance('‹ bar') == 'bar'
    assert clean_utterance('› bar') == 'bar'
    assert clean_utterance('[*] bar') == 'bar'
    assert clean_utterance('bar [*]') == 'bar'


def test_get_participant_code():
    assert get_participant_code({'CHI', '%mor', '%gra'}) == 'CHI'
    assert get_participant_code({'MOT', '%mor', '%gra'}) == 'MOT'


def test_clean_word():
    assert clean_word('foo') == 'foo'
    assert clean_word('&foo') == 'foo'
    assert clean_word('foo@bar') == 'foo'
    assert clean_word('foo(') == 'foo'
    assert clean_word('foo)') == 'foo'
    assert clean_word('foo:') == 'foo'
    assert clean_word('foo;') == 'foo'
    assert clean_word('foo+') == 'foo'


def test_convert_date_to_tuple():
    assert convert_date_to_tuple('01-FEB-2016') == (2016, 2, 1)


def test_get_lemma_from_mor():
    assert get_lemma_from_mor('foo&bar-baz') == 'foo'


def test_remove_extra_spaces():
    assert remove_extra_spaces('foo  bar') == 'foo bar'
    assert remove_extra_spaces('foo bar  baz') == 'foo bar baz'


def test_find_indices():
    assert find_indices('foo bar', 'foo') == [0]
    assert find_indices('foo foo bar', 'foo') == [0, 4]
    assert find_indices('foo bar foo', 'foo') == [0, 8]
    assert find_indices('foo bar baz', 'bar') == [4]
