from classes.GraphQW import GraphQW
import methods.indirect_influence as ii
import methods.direct_influence as di
import networkx as nx


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
