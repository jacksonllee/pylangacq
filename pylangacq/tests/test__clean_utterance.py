import pytest

from pylangacq._clean_utterance import _clean_utterance


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
        ("foo [: bar] [/]", ""),
        ("< blah foo > [: bar] [/]", ""),
        ("foo [: bar blah] [/]", ""),
        ("< blah foo > [: bar haha] [/]", ""),
    ],
)
def test__clean_utterance(original, expected):
    # TODO: Most of step 3 and all of step 5 in the function not tested
    assert _clean_utterance(original) == expected
