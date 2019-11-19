from classes.GraphQW import GraphQW, nx
import methods.indirect_influence as ii
import methods.direct_influence as di
import methods.netsim as ns


def lric(graph, q=50, dq=None, group_size=None, size=None, limpath=3, models='max', data=False):
    """
    LRIC centrality
    :param graph: (Graph/DiGraph), input graph (NetworkX package)
    :param q: (float, optional), quota (threshold of influence) for each node (share of weighted in-degree).
                                 By default q = 50% of node's weighted in-degree.
    :param dq: (float/array/dict, optional), predefined fixed threshold value for each node.
    :param group_size: (int, optional), maximal group size (cardinality of coalition).
    :param size: (float/array/dict, optional), nodes size (float, array or dictionary).
                                          By default node size is equal to weighted out-degree.
    :param limpath: (int, optional), maximal length of influence.
    :param models: (str/array, optional), type of LRIC centrality (max, maxmin, pagerank).
                                      By default models = "max"
    :param data: (bool): logical scalar. If the data arguments is False, then nodes centrality is returned.
                                    Otherwise, centrality and LRIC graph is returned. By default data = false.
    :return:
            ranking (dict): nodes LRIC centrality (dictionary)
            g (GraphQW) - LRIC graph
    """
    if isinstance(models, str):
        models = [models]
    if group_size is None:
        group_size = len(graph.nodes()) - 1
    ranking = dict()
    g = di.pairwise_inf(GraphQW(graph, q, dq, group_size, size), method='LRIC')  # evaluate direct influence
    if 'pagerank' in models:  # calculate LRIC PageRank
        ranking = ii.indirect_pagerank(g).aggregate()
        g.set_param('lric_pagerank', ranking)
    if 'max' in models:  # calculate LRIC_Max
        ranking = ii.indirect_paths(g, limpath, 0, 2).aggregate()
        g.set_param('lric_max', ranking)
    if 'maxmin' in models:
        ranking = ii.indirect_paths(g, limpath, 0, 1).aggregate()
        g.set_param('lric_maxmin', ranking)
    if data:
        return ranking, g
    else:
        return ranking


def sric(graph, q=50, dq=None, group_size=4, size=None, data=False):
    """
    SRIC centrality
    :param graph: (Graph/DiGraph), input graph (NetworkX package)
    :param q: (float, optional), quota (threshold of influence) for each node (share of weighted in-degree).
                                 By default q = 50% of node's weighted in-degree.
    :param dq: (float/array/dict, optional), predefined fixed threshold value for each node.
    :param group_size: (int, optional), maximal group size (cardinality of coalition). By default limcoal = 4.
    :param size: (float/array/dict, optional), nodes size (float, array or dictionary).
                                          By default node size is equal to weighted out-degree.
    :param data: (bool): logical scalar. If the data arguments is False, then nodes centrality is returned.
                                    Otherwise, centrality and LRIC graph is returned. By default data = false.
    :return:
            ranking (dict): nodes SRIC centrality (dictionary)
            g (GraphQW) - SRIC graph
    """
    g = di.pairwise_inf(GraphQW(graph, q, dq, group_size, size), method='SRIC')  # calculate SRIC graph
    ranking = g.aggregate(name='sric')  # calculate centrality of each node
    if data:
        return ranking, g
    else:
        return ranking


def graphsim(graph1, graph2, r1=None, r2=None, eps=0.05, eps_method=1, edge_name="weight", topology_type=0):
    """
    :param graph1: graph 1
    :param graph2: graph 2
    :param r1: ranking in graph 1
    :param r2: ranking in graph 2
    :param eps: measurement error
    :param eps_method: method for interval construction (o - absolute, 1 - relative)
    :param edge_name: compared edge attribute
    :param topology_type: topology distance normalization method
    :return: topology and ranking distance
    """
    if r1 is None or r2 is None:
        res1 = lric(graph1, data=True)
        res2 = lric(graph2, data=True)
        rank_dist = ns.rank_dist(res1[0], res2[0], eps, eps_method)
        top_dist = ns.top_dist(res1[1], res2[1], edge_name, topology_type)
    else:
        rank_dist = ns.rank_dist(r1, r2, eps, eps_method)
        top_dist = ns.top_dist(graph1, graph2, edge_name, topology_type)
    return top_dist, rank_dist


def interdependence(graph, q=50, dq=None, group_size=None, size=None, limpath=3, model=3, data=False):
    """
    Interdependence centrality
    :param graph: (Graph/DiGraph), input graph (NetworkX package)
    :param q: (float, optional), quota (threshold of influence) for each node (share of weighted in-degree).
                                 By default q = 50% of node's weighted in-degree.
    :param dq: (float/array/dict, optional), predefined fixed threshold value for each node.
    :param group_size: (int, optional), maximal group size (cardinality of coalition). By default limcoal = 3.
    :param size: (float/array/dict, optional), nodes size (float, array or dictionary).
                                          By default node size is equal to weighted out-degree.
    :param limpath: (int, optional), maximal length of influence.
    :param model: model of indirect influence (according to the paper), By default model = 4.
    :param data: (bool): logical scalar. If the data arguments is False, then nodes centrality is returned.
                                    Otherwise, centrality and LRIC graph is returned. By default data = false.
    :return:
            ranking (dict): nodes interdependence centrality (dictionary)
            g (GraphQW) - interdependence graph
    """
    edge_name = 'weight'

    if group_size is None:
        group_size = len(graph.nodes()) - 1
    if isinstance(q, float) or isinstance(q, int) or q is None:
        q = [q, q]
    if isinstance(dq, dict) or isinstance(dq, float) or isinstance(dq, int) or dq is None:
        dq = [dq, dq]
    if isinstance(size, dict)or isinstance(size, float) or isinstance(size, int) or size is None:
        size = [size, size]
    inf_g = di.pairwise_inf(GraphQW(graph, q[0], dq[0], group_size, size[0]), method='LRIC')  # define direct influence
    dep_g = di.pairwise_inf(GraphQW(nx.reverse(graph), q[1], dq[1],
                                    group_size, size[1]), method='LRIC')  # define direct dependence

    if model == 1:  # model 1: nodes interdependence as aggregation of indirect influences
        indirect1 = ii.indirect_paths(inf_g, limpath, 0, 2)
        indirect2 = ii.indirect_paths(dep_g, limpath, 0, 2)
        for edge in indirect2.edges(data=True):
            if indirect1.has_edge(edge[0], edge[1]) and edge[2][edge_name] > indirect1[edge[0]][edge[1]][edge_name]:
                indirect1[edge[0]][edge[1]][edge_name] = edge[2][edge_name]
            else:
                indirect1.add_edge(edge[0], edge[1], weight=edge[2][edge_name])
        g = indirect1.copy()
    elif model == 2:  # model 2: nodes interdependence based on difference of direct influences
        for edge in dep_g.edges(data=True):
            if inf_g.has_edge(edge[0], edge[1]):
                inf_g[edge[0]][edge[1]][edge_name] += edge[2][edge_name]
            else:
                inf_g.add_edge(edge[0], edge[1], weight=edge[2][edge_name])
        for edge in inf_g.edges(data=True):
            v = edge[2][edge_name]
            if inf_g.has_edge(edge[1], edge[0]):
                v -= inf_g[edge[1]][edge[0]][edge_name]
            if v >= 0:
                inf_g[edge[0]][edge[1]][edge_name] = v
                if inf_g.has_edge(edge[1], edge[0]):
                    inf_g[edge[1]][edge[0]][edge_name] = 0
            else:
                inf_g[edge[0]][edge[1]]['weight'] = 0
                inf_g[edge[1]][edge[0]]['weight'] = (-1 * v)
            if inf_g[edge[0]][edge[1]]['weight'] > 1:
                inf_g[edge[0]][edge[1]]['weight'] = 1
        g = ii.indirect_paths(inf_g, limpath, 0, 2)
    elif model == 3:  # model 3: nodes interdependence as a search for influential paths
        g = ii.indirect_bipath([inf_g, dep_g], ii.create_quality(inf_g, dep_g), limpath)[1]

    if data:
        return g.aggregate(), g
    else:
        return g.aggregate()
