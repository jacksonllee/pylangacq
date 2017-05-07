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

        :return: The LaTeX tikz-dependency code for drawing the graph

        :rtype: str
        """
        tikz_dep_code = ''

        # get graph info
        dep_to_head = dict(self.edges())
        number_of_nodes = self.number_of_nodes()

        # add \begin{deptext}...\end{deptext}
        words = [self.node[n]['word']
                 for n in range(1, number_of_nodes)]
        deptext_template = '    \\begin{{deptext}}[column sep=1em]\n' + \
                           '        {} \\\\ \n' + \
                           '    \\end{{deptext}}\n'
        tikz_dep_code += deptext_template.format(' \\& '.join(words))

        # add the \deproot line
        dep_shooting_to_root = 0
        root_rel = ''
        for dep in range(1, number_of_nodes):
            head = dep_to_head[dep]
            if head == 0:
                dep_shooting_to_root = dep
                root_rel = self.edge[dep_shooting_to_root][0]['rel']
                break
        tikz_dep_code += '    \\deproot{{{}}}{{{}}}\n'.format(
            dep_shooting_to_root, root_rel)

        # add the \depedge lines
        for dep in range(1, number_of_nodes):
            head = dep_to_head[dep]
            rel = self.edge[dep][head]['rel']
            tikz_dep_code += '    \\depedge{{{}}}{{{}}}{{{}}}\n'.format(
                dep, head, rel)

        # return tikz_dep_code
        # wrapped inside \begin{dependency}...\end{dependency}
        dependency_template = '\\begin{{dependency}}[theme = simple]\n' + \
                              '{}\\end{{dependency}}'
        return dependency_template.format(tikz_dep_code)

    def to_conll(self):
        """
        Return the dependency graph in the CoNLL format.

        :return: The CoNLL format of the dependency graph

        :rtype: str
        """
        collector = list()
        dep_to_head = dict(self.edges())

        for dep in range(1, self.number_of_nodes()):
            head = dep_to_head[dep]
            word = self.node[dep]['word']
            pos = self.node[dep]['pos']
            rel = self.edge[dep][head]['rel']
            collector.append('{} {} {} {}'.format(word, pos, head, rel))

        return '\n'.join(collector)
