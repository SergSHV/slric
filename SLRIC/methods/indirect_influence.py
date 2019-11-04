from math import isclose
from classes.GraphQW import GraphQW, nx


# Calculate indirect influence by random walks (Personalized PageRank)
def indirect_pagerank(g):
    g_lric = GraphQW()  # Create Graph that stores information about indirect influence
    g_lric.add_nodes_from(g.nodes(data=True))  # Copy all nodes from initial graph
    nodes_degree = g.out_degree(weight='weight')  # Calculate out-degree for each node
    nodes_num = len(nodes_degree)  # Total number of nodes
    components = nx.weakly_connected_components(g)  # Find all components in a graph
    for comp in components:
        if len(comp) > 1:  # check if component contains more than 1 element
            sub_graph = g.subgraph(comp).copy()  # consider each component individually
            pers = dict(zip(comp, [0] * nodes_num))
            for node in comp:
                if nodes_degree[node] > 0:
                    g1 = sub_graph.copy()
                    pers[node] = 1
                    for node2 in comp: # add necessary edges
                            if g1.has_edge(node2, node):
                                g1[node2][node]['weight'] += nodes_num - nodes_degree[node2] - 1
                            else:
                                g1.add_edge(node2, node, weight=nodes_num - nodes_degree[node2] - 1)
                    lric_pr = nx.pagerank(g1, personalization=pers)  # calculate PageRank
                    for node2 in lric_pr:  # add results
                        if not isclose(lric_pr[node2], 0) and node != node2:
                            g_lric.add_edge(node, node2, weight=lric_pr[node2])
                    pers[node] = 0
    return g_lric


# Find all paths of length <= path_lim (fast multiplication implementation)
def indirect_paths(g, path_lim, aggregation, criterion):
    if path_lim == 1:  # path length is 1
        return g
    else:  # find all paths
        if path_lim % 2 == 0:
            return indirect_paths(compute_path(g, g, aggregation, criterion), path_lim // 2, type, criterion)
        else:
            return compute_path(indirect_paths(g, path_lim - 1, aggregation, criterion), g, type, criterion)


# Evaluate path strength [criterion: 0 (sum), 1 (min), 2 (multiplication)]
def define_weight(w1, w2, criterion):
    if criterion == 0:
        return w1 + w2
    elif criterion == 1:
        return min(w1, w2)
    else:
        return w1*w2


# Aggregate paths using g0 and g1 [aggregation: 0 (maxPath), 1 (sumPaths)]
def compute_path(g0, g1, aggregation, criterion):
    g = g0.copy()
    g.add_nodes_from(g0.nodes(data=True))
    for node in g0.node():
            for node2 in g0.successors(node):
                for node3 in g1.successors(node2):  # node -> node2 -> node3
                    w = define_weight(g0[node][node2]['weight'], g1[node2][node3]['weight'], criterion)  # path weight
                    if g.has_edge(node, node3):  # add edge to graph
                        if aggregation == 0:
                            if w > g[node][node3]['weight']:
                                g[node][node3]['weight'] = w
                        else:
                            g[node][node3]['weight'] += w
                    else:
                        g.add_edge(node, node3, weight=w)
    return g
