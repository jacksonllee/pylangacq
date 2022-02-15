from pylangacq.measures import _get_lemma_from_mor


def test__get_lemma_from_mor():
    assert _get_lemma_from_mor("foo&bar-baz") == "foo"
