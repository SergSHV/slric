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
            return indirect_paths(compute_path(g, g, aggregation, criterion), path_lim // 2, aggregation, criterion)
        else:
            return compute_path(indirect_paths(g, path_lim - 1, aggregation, criterion), g, aggregation, criterion)


# Evaluate path strength [criterion: 0 (sum), 1 (min), 2 (multiplication)]
def define_weight(w1, w2, criterion):
    if criterion == 0:
        return w1 + w2
    elif criterion == 1:
        return min(w1, w2)
    else:
        return w1*w2


# Update weights in a graph
def update_weight(g, node1, node2, v, name, criterion=0):
    chk = True  # check if edge weight is updated in a graph
    if not g.has_edge(node1, node2):  # edge does not exist in graph g
        if v > 0:  # edge weight v is positive
            g.add_edge(node1, node2, weight=v)
    elif (v > g[node1][node2][name] or criterion != 0) and v > 0:  # update if v is positive and v > edge weight
        g[node1][node2][name] = v
    else:
        chk = False
    return g, chk


# Aggregate paths using g0 and g1 [aggregation: 0 (maxPath), 1 (sumPaths)]
def compute_path(g0, g1, aggregation, criterion):
    g = g0.copy()
    g.add_nodes_from(g0.nodes(data=True))
    for node in g0.nodes():
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


# Update paths with more strengths
def update_bipath(quality, list_g, list_g0, list_g1, node, nodes_list, criterion, name, index=0):
    for node2 in nodes_list:
        for node3 in list_g1[index].successors(node2):  # node -> node2 -> node3
            if node3 != node:
                w0, w1 = 0, 0
                w0 = define_weight(list_g0[index][node][node2][name], list_g1[index][node2][node3][name], criterion)
                if list_g0[1-index].has_edge(node2, node) and list_g1[1-index].has_edge(node3, node2):
                    w1 = define_weight(list_g0[1-index][node2][node][name],
                                       list_g1[1-index][node3][node2][name], criterion)
                if w0 - w1 >= 0:
                    res = update_weight(quality, node, node3, w0 - w1, name)
                else:
                    res = update_weight(quality, node3, node, w1 - w0, name)
                if res[1]:
                    quality = res[0]
                    list_g[index] = update_weight(list_g[index], node, node3, w0, name, 1)[0]
                    list_g[1-index] = update_weight(list_g[1-index], node3, node, w1, name, 1)[0]
    return list_g, quality


# Aggregate paths using multilayer g0 and g1
def compute_bipath(list_g0, list_g1, quality, criterion, name):
    list_g = [list_g0[0].copy(), list_g1[1].copy()]
    list_g[0].add_nodes_from(list_g0[1].nodes())
    list_g[1].add_nodes_from(list_g1[0].nodes())
    nodes_list = list_g[0].nodes()

    for node in nodes_list:
        # do for adjacent nodes in g1 (influence layer)
        list_g, quality = update_bipath(quality, list_g, list_g0, list_g1, node, set(list_g0[0].neighbors(node)), criterion, name, 0)
        # do for adjacent nodes in g1 (dependance layer)
        list_g, quality = update_bipath(quality, list_g, list_g0, list_g1, node, set(list_g0[1].neighbors(node)), criterion, name, 1)
    return list_g, quality


# Find all paths of length <= path_lim (fast multiplication implementation)
def indirect_bipath(list_g, quality, path_lim, criterion=2, name='weight'):
    if path_lim == 1:  # path length is 1
        return list_g, create_quality(list_g[0], list_g[1], quality, name)
    else:  # find all paths
        if path_lim % 2 == 0:
            res = compute_bipath(list_g, list_g, quality, criterion, name)
            return indirect_bipath(res[0], res[1], path_lim // 2, criterion, name)
        else:
            res = indirect_bipath(list_g, quality, path_lim - 1, criterion, name)
            return compute_bipath(res[0], list_g, res[1], criterion, name)


# Define current bi-path strengths
def create_quality(g1, g2, quality=None, name='weight'):
    if quality is None:
        quality = nx.create_empty_copy(g1)

    nodes_list = set(g1.nodes()) | set(g2.nodes())
    for node in nodes_list:
        nodes1 = set(g1.neighbors(node))  # adjacent nodes in g1
        nodes2 = set(g2.predecessors(node)) - nodes1  # distinct adjacent nodes in g2
        for node2 in nodes1:
            v = g1[node][node2][name]
            if node2 in g2.predecessors(node):
                v -= g2[node2][node][name]
            if v > 0:
                quality = update_weight(quality, node, node2, v, name)[0]
            elif v < 0:
                quality = update_weight(quality, node2, node, -v, name)[0]
            for node2 in nodes2:
                quality = update_weight(quality, node2, node, g2[node2][node][name], name)[0]
    return quality
