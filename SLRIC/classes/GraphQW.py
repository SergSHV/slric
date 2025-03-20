import networkx as nx
import networkx.convert as convert


# Class "GraphQW" is a NetworkX graph with generated individual attributes
class GraphQW(nx.DiGraph):
    def __init__(self, g = None, q = None, dq = None, limcoal = None, dw = None):
        self.graph = {}
        self._node = self.node_dict_factory()
        self._adj = self.adjlist_outer_dict_factory()  # empty adjacency dict
        self._pred = self.adjlist_outer_dict_factory()  # predecessor
        self._succ = self._adj  # successor
        if g is not None:
            self.graph.update(g.graph)
            self._node.update((n, dd.copy()) for n, dd in g.nodes.items())
            self._adj.update(g._adj)
            if not nx.is_directed(g):
                g = nx.DiGraph(g)
            self._pred.update(g._pred)
            self._succ.update(g._succ)

            nx.set_node_attributes(self, name='indeg', values=dict(self.in_degree(weight='weight')))
            self.set_quota(q, dq)
            self.set_size(dw)
            self.coal = limcoal
            for edge in self.edges(data = True):
                if 'weight' not in edge[2]:
                    self.set_edge_attr('weight', 1)
                break


    def set_edge_attr(self, name, value):
        edges = self.edges()
        edge_list = dict(zip(edges, [value] * len(edges)))
        nx.set_edge_attributes(self, edge_list, name)

    def set_size(self, dw):
        if dw is None:
            pp = self.out_degree(weight='weight')
            nx.set_node_attributes(self, name='size', values=dict(self.out_degree(weight='weight')))
        else:
            self.set_param('size', dw)

    def set_quota(self, q, dq):
        if dq is None:
            ql = dict()
            d = self.in_degree(weight='weight')
            for x, y in d:
                ql[x] = y * q / 100
            nx.set_node_attributes(self, name='q', values=ql)
        else:
            self.set_param('q', dq)

    def set_param(self, name, data):
        if data is not None:
            if isinstance(data, dict):
                nx.set_node_attributes(self, name=name, values=data)
            elif isinstance(data, list):
                if len(self.nodes()) == len(data):
                    nx.set_node_attributes(self, name=name, values=dict(zip(self.nodes(), data)))
            elif isinstance(data, float) or isinstance(data, int):
                nx.set_node_attributes(self, name=name, values=dict(zip(self.nodes(), [data] * len(self.nodes()))))

    def aggregate(self, name=''):
        pers = dict(zip(self.nodes(), [0] * len(self)))
        for edge in self.edges(data=True):
            if edge[0] != edge[1]:
                pers[edge[0]] += self.nodes[edge[1]]['size']*edge[2]['weight']
        pers = self.normalize(pers)
        self.set_param(name, pers)
        return pers

    @staticmethod
    def normalize(arr):
        s = sum(arr.values())
        if s != 0:
            for el in arr:
                arr[el] /= s
        return arr

    def write_centrality(self, filename, separator=';', mode='a+', additional_attr=[], additional_headers=[]):
        """
        Write SRIC/LRIC centrality to file
        :param filename: filename
        :param separator: line separator
        :param mode: mode while opening a file. If not provided, it defaults to 'a' (append)
        :param additional_attr: list of additional parameters which will be appended to each line
        :param additional_headers: headers of additional parameters
        :return: None
        """
        self.write(self.nodes(data=True), filename, separator, mode, 1, additional_attr, additional_headers)

    def write_edgelist(self, filename, separator=';', mode='a+', additional_attr=[], additional_headers=[]):
        """
        Write edges from SRIC/LRIC graph to file
        :param filename: filename
        :param separator: line separator
        :param mode: mode while opening a file. If not provided, it defaults to 'a' (append)
        :param additional_attr: list of additional parameters which will be appended to each line
        :param additional_headers: headers of additional parameters
        :return:
        """
        self.write(self.edges(data=True), filename, separator, mode, 0, additional_attr, additional_headers)

    @staticmethod
    def write(row_dict, filename, separator=';', mode='a+', type_header=0, additional_attr=[], additional_headers=[]):
        f = open(filename, mode)
        lim = 1000
        arr = []
        if type_header == 0:
            arr.append(separator.join(additional_headers+['From', 'To', 'Edge Type', 'Value']))
        elif type_header == 1:
            arr.append(separator.join(['Node', 'Centrality', 'Value']))
        for row in row_dict:
            for attr in row[-1]:
                if attr not in ['indeg', 'q', 'size']:
                    if len(row) == 3:
                        arr.append(separator.join(additional_attr+[str(row[0]), str(row[1]), attr, str(row[2][attr])]))
                    else:
                        arr.append(separator.join(additional_attr+[str(row[0]), attr, str(row[1][attr])]))
                    if len(arr) > lim:
                        f.write('\n'.join(arr))
                        arr = []
        f.write('\n'.join(arr))
