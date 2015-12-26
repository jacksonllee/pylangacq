import networkx as nx

class DependencyGraph(nx.DiGraph):
    """
    DependencyGraph is a class based on the networkx directed graph for
    modeling dependency graphs in dependency grammar.
    """
    def to_tikz(self):
        """

        :return: The LaTeX tikz-dependency code for drawing the graph
        :rtype: str
        """
        return  # work in progress
