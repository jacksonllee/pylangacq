import pytest

from pylangacq.util import (
    clean_utterance,
    get_participant_code,
    clean_word,
    convert_date_to_tuple,
    get_lemma_from_mor,
    remove_extra_spaces,
    find_indices,
)


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
    ],
)
def test_clean_utterance(original, expected):
    # TODO: Steps 3 and 5 in the function not tested
    assert clean_utterance(original) == expected


@pytest.mark.parametrize(
    "keys, expected",
    [({"CHI", "%mor", "%gra"}, "CHI"), ({"MOT", "%mor", "%gra"}, "MOT")],
)
def test_get_participant_code(keys, expected):
    assert get_participant_code(keys) == expected


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
def test_clean_word(original, expected):
    assert clean_word(original) == expected


def test_convert_date_to_tuple():
    assert convert_date_to_tuple("01-FEB-2016") == (2016, 2, 1)


def test_get_lemma_from_mor():
    assert get_lemma_from_mor("foo&bar-baz") == "foo"


@pytest.mark.parametrize(
    "original, expected",
    [("foo  bar", "foo bar"), ("foo bar  baz", "foo bar baz")],
)
def test_remove_extra_spaces(original, expected):
    assert remove_extra_spaces(original) == expected


@pytest.mark.parametrize(
    "original, target, expected",
    [
        ("foo bar", "foo", [0]),
        ("foo foo bar", "foo", [0, 4]),
        ("foo bar foo", "foo", [0, 8]),
        ("foo bar baz", "bar", [4]),
    ],
)
def test_find_indices(original, target, expected):
    assert find_indices(original, target) == expected
