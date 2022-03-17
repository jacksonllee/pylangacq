from pylangacq.tests.test_chat import _EXPECTED_EVE_UTTERANCES


def test_utterance_to_str_tabular_false():
    actual = _EXPECTED_EVE_UTTERANCES[0]._to_str(tabular=False)
    expected = (
        "*CHI:\tmore cookie . [+ IMP]\n"
        "%mor:\tqn|more n|cookie .\n"
        "%gra:\t1|2|QUANT 2|0|INCROOT 3|2|PUNCT\n"
        "%int:\tdistinctive , loud\n"
    )
    assert actual == expected


def test_utterance_to_str_tabular_true():
    actual = _EXPECTED_EVE_UTTERANCES[0]._to_str(tabular=True)
    expected = (
        "*CHI:  more       cookie       .\n"
        "%mor:  qn|more    n|cookie     .\n"
        "%gra:  1|2|QUANT  2|0|INCROOT  3|2|PUNCT\n"
        "%int:\tdistinctive , loud\n"
    )
    assert actual == expected
