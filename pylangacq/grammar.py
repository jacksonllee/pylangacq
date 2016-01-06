# -*- coding: utf-8 -*-

import networkx as nx


class DependencyGraph(nx.DiGraph):
    """
    DependencyGraph is a class based on the networkx directed graph for
        modeling dependency graphs in dependency grammar.
    """
    def __init__(self, data, form='CHAT'):
        """
        Initialize dependency graph.

        :param data: input data

        :param form: format of the input data
        """
        super(DependencyGraph, self).__init__()
        self.data = data
        self._faulty = False

        if form == 'CHAT':
            self._create_graph_from_chat()
        else:
            raise ValueError('invalid graph data format: {}'.format(form))

    def _create_graph_from_chat(self):
        """
        Create dependency graph based on the input data.
        """
        for word, pos, mor, gra in self.data:
            try:
                node1, node2, relation = gra  # e.g., (1, 3, 'LINK')
            except ValueError:
                node1 = -1
                node2 = -1
                relation = '**ERROR**'
                self._faulty = True

            self.add_edge(node1, node2, rel=relation)
            self.node[node1] = {'word': word,
                                'pos': pos,
                                'mor': mor,
                                }

        self.node[0] = {'word': 'ROOT',
                        'pos': 'ROOT',
                        'mor': 'ROOT',
                        }

    def faulty(self):
        """
        Return True or False for whether the graph is faulty for dependency
            information.

        :return: True or False
        """
        return self._faulty

    def to_tikz(self):
        """
        Return the dependency graph as LaTeX tikz-dependency code.

        >>> graph = DependencyGraph(chat_graph_data)
        >>> graph.to_tikz()
        \begin{dependency}[theme = simple]
           \begin{deptext}[column sep=1em]
              but \& I \& thought \& you \& wanted \& me \& to \& turn \& it \& . \\
           \end{deptext}
           \deproot{3}{ROOT}
           \depedge{1}{3}{LINK}
           \depedge{2}{3}{SUBJ}
           \depedge{4}{3}{OBJ}
           \depedge{5}{3}{JCT}
           \depedge{6}{5}{POBJ}
           \depedge{7}{8}{INF}
           \depedge{8}{3}{XCOMP}
           \depedge{9}{8}{OBJ}
           \depedge{10}{3}{PUNCT}
        \end{dependency}

        :return: The LaTeX tikz-dependency code for drawing the graph

        :rtype: str
        """
        return  # work in progress

    def to_conll(self):
        """
        Return the dependency graph in the CoNLL format.

        >>> graph = DependencyGraph(chat_graph_data)
        >>> graph.to_conll()
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

        :return: The CoNLL format of the dependency graph

        :rtype: str
        """
        return  # work in progress


chat_graph_data = [('but', 'CONJ', 'but', (1, 3, 'LINK')),
                   ('I', 'PRO:SUB', 'I', (2, 3, 'SUBJ')),
                   ('thought', 'V', 'think&PAST', (3, 0, 'ROOT')),
                   ('you', 'PRO', 'you', (4, 3, 'OBJ')),
                   ('wanted', 'V', 'want-PAST', (5, 3, 'JCT')),
                   ('me', 'PRO:OBJ', 'me', (6, 5, 'POBJ')),
                   ('to', 'INF', 'to', (7, 8, 'INF')),
                   ('turn', 'V', 'turn', (8, 3, 'XCOMP')),
                   ('it', 'PRO', 'it', (9, 8, 'OBJ')),
                   ('.', '.', '', (10, 3, 'PUNCT')),
                   ]

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
