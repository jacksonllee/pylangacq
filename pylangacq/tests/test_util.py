# -*- coding: utf-8 -*-

from pylangacq.util import clean_utterance


def test_clean_utterance():
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
