from pylangacq.dependency import DependencyGraph


_CHAT_GRAPH_DATA = [
    ("but", "CONJ", "but", (1, 3, "LINK")),
    ("I", "PRO:SUB", "I", (2, 3, "SUBJ")),
    ("thought", "V", "think&PAST", (3, 0, "ROOT")),
    ("you", "PRO", "you", (4, 3, "OBJ")),
    ("wanted", "V", "want-PAST", (5, 3, "JCT")),
    ("me", "PRO:OBJ", "me", (6, 5, "POBJ")),
    ("to", "INF", "to", (7, 8, "INF")),
    ("turn", "V", "turn", (8, 3, "XCOMP")),
    ("it", "PRO", "it", (9, 8, "OBJ")),
    (".", ".", "", (10, 3, "PUNCT")),
]


def test_dep_graph_to_tikz():
    graph = DependencyGraph(_CHAT_GRAPH_DATA)
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
    graph = DependencyGraph(_CHAT_GRAPH_DATA)
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
