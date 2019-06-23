from classes.GraphQW import GraphQW
import methods.indirect_influence as ii
import methods.direct_influence as di
import methods.netsim as ns


def lric(graph, q=20, dq=None, group_size=4, size=None, limpath=3, models='max', data=False):
    """
    LRIC centrality
    :param graph: (Graph/DiGraph), input graph (NetworkX package)
    :param q: (float, optional), quota (threshold of influence) for each node (share of weighted in-degree).
                                 By default q = 20% of node's weighted in-degree.
    :param dq: (float/array/dict, optional), predefined fixed threshold value for each node.
    :param group_size: (int, optional), maximal group size (cardinality of coalition). By default limcoal = 4.
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


def sric(graph, q=20, dq=None, group_size=4, size=None, data=False):
    """
    SRIC centrality
    :param graph: (Graph/DiGraph), input graph (NetworkX package)
    :param q: (float, optional), quota (threshold of influence) for each node (share of weighted in-degree).
                                 By default q = 20% of node's weighted in-degree.
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


def graphsim(graph1, graph2, r1=None, r2=None, eps=0.05, method=1, edge_name="weight"):
    """
    :param graph1: graph 1
    :param graph2: graph 2
    :param r1: ranking in graph 1
    :param r2: ranking in graph 2
    :param eps: measurement error
    :param method: method for interval construction (o - absolute, 1 - relative)
    :param edge_name: compared edge attribute
    :return: topology and ranking distance
    """
    if r1 is None or r2 is None:
        res1 = lric(graph1, data=True)
        res2 = lric(graph2, data=True)
        rank_dist = ns.rank_dist(res1[0], res2[0], eps, method)
        top_dist = ns.top_dist(res1[1], res2[1], edge_name)
    else:
        rank_dist = ns.rank_dist(r1, r2, eps, method)
        top_dist = ns.top_dist(graph1, graph2, edge_name)
    return top_dist, rank_dist
