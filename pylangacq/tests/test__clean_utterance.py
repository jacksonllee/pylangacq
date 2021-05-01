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
        ("foo [:: bar]", "foo"),
        ("foo [:: bar baz]", "foo"),
        ("<foo baz> [:: bar]", "foo baz"),
        ("<foo baz> [:: bar boo]", "foo baz"),
        ("a ↫ch-ch↫xxx .", "a ."),  # CHILDES -> Clinical-MOR -> EllisWeismer
        ("this [!!] [//] that", "that"),  # CHILDES -> Eng-NA -> Bloom
        ("we're [/?] [/] we're", "we're"),  # CHILDES -> Eng-NA -> NewmanRatner
        ("a xxx→", "a"),  # CHILDES -> Eng-NA -> Sprott
        ("a [/] [//] a lady", "a lady"),  # CHILDES -> Eng-UK -> Thomas
        ("house (1:19.) .", "house ."),  # CHILDES -> Eng-UK -> Wells
        ("xxx; crocodile", "crocodile"),  # CHILDES -> French -> Champaud
        ("foo [^c] bar", "foo bar"),  # clause delimiter
        ("xxx↑ foo", "foo"),  # CHILDES -> Frogs -> English-Slobin
        ("no: [!!] [//] (..) ey", "ey"),  # CHILDES -> Spanish -> Montes
        ("⌈foo bar⌉", "foo bar"),  # overlapping markers
        ("⌈ foo bar ⌉", "foo bar"),  # overlapping markers
        ("foo.", "foo ."),
        ("+...", "+..."),
    ],
)
def test__clean_utterance(original, expected):
    # TODO: Most of step 3 and all of step 5 in the function not tested
    assert _clean_utterance(original) == expected
