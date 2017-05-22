# -*- coding: utf-8 -*-


class DependencyGraph(object):
    """
    DependencyGraph is a class representing dependency graphs in dependency
        grammar.
    """
    def __init__(self, data):
        """
        Initialize dependency graph.

        :param data: input data

        :param form: format of the input data
        """
        self.node = {}  # from node to dict (node's properties)
        self.edge = {}  # from node to node to dict (edge's properties)

        self.data = data
        self._faulty = False

        self._create_graph_from_chat()

    def add_edge(self, node1, node2, **kwargs):
        if node1 not in self.node:
            self.node[node1] = {}
        if node2 not in self.node:
            self.node[node2] = {}

        if node1 not in self.edge:
            self.edge[node1] = {}
        self.edge[node1][node2] = kwargs

    def edges(self):
        result = {}
        for node1, node2_to_properties in self.edge.items():
            for node2 in node2_to_properties.keys():
                result[node1] = node2
        return result

    def number_of_nodes(self):
        return len(self.node)

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
