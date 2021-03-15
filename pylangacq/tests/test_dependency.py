from pylangacq.dependency import _DependencyGraph
from pylangacq.objects import Gra, Token


_CHAT_GRAPH_DATA = [
    Token("but", "CONJ", "but", Gra(1, 3, "LINK")),
    Token("I", "PRO:SUB", "I", Gra(2, 3, "SUBJ")),
    Token("thought", "V", "think&PAST", Gra(3, 0, "ROOT")),
    Token("you", "PRO", "you", Gra(4, 3, "OBJ")),
    Token("wanted", "V", "want-PAST", Gra(5, 3, "JCT")),
    Token("me", "PRO:OBJ", "me", Gra(6, 5, "POBJ")),
    Token("to", "INF", "to", Gra(7, 8, "INF")),
    Token("turn", "V", "turn", Gra(8, 3, "XCOMP")),
    Token("it", "PRO", "it", Gra(9, 8, "OBJ")),
    Token(".", ".", "", Gra(10, 3, "PUNCT")),
]


def test_dep_graph_to_tikz():
    graph = _DependencyGraph(_CHAT_GRAPH_DATA)
    assert (
        graph.to_tikz()
        == """
\\begin{dependency}[theme = simple]
    \\begin{deptext}[column sep=1em]
        but \\& I \\& thought \\& you \\& wanted \\& me \\& to \\& turn \\& it \\& . \\\\ 
    \\end{deptext}
    \\deproot{3}{ROOT}
    \\depedge{1}{3}{LINK}
    \\depedge{2}{3}{SUBJ}
    \\depedge{3}{0}{ROOT}
    \\depedge{4}{3}{OBJ}
    \\depedge{5}{3}{JCT}
    \\depedge{6}{5}{POBJ}
    \\depedge{7}{8}{INF}
    \\depedge{8}{3}{XCOMP}
    \\depedge{9}{8}{OBJ}
    \\depedge{10}{3}{PUNCT}
\\end{dependency}
""".strip()  # noqa
    )


def test_dep_graph_to_conll():
    graph = _DependencyGraph(_CHAT_GRAPH_DATA)
    assert (
        graph.to_conll()
        == """
but CONJ 3 LINK
I PRO:SUB 3 SUBJ
thought V 0 ROOT
you PRO 3 OBJ
wanted V 3 JCT
me PRO:OBJ 5 POBJ
to INF 8 INF
turn V 3 XCOMP
it PRO 8 OBJ
. . 3 PUNCT
""".strip()
    )
