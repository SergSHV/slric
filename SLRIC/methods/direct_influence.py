from math import ceil, isclose
import numpy as np
from classes.GraphQW import GraphQW
from methods.sric import define_sric, generate_sric_matrix
from methods.lric import find_lp


# Calculation of SRIC and LRIC direct influence
def pairwise_inf(g, method):
    dirgraph = GraphQW()
    nodes_list = g.nodes(data=True)
    dirgraph.add_nodes_from(nodes_list)  # copy list of nodes
    for node in nodes_list:
        if 'q' in node[1] and node[1]['indeg'] >= node[1]['q'] > 0 and g.coal > 0:  # node can be affected, quota is non-zero
            inf_list = []
            if method == 'LRIC':  # evaluate LRIC influence
                inf_list = individual_lric(g.in_edges(node[0], data=True), node[1]['q'], g.coal)
            elif method == 'SRIC':  # evaluate SRIC influence
                inf_list = individual_sric(g, node[0], node[1]['q'], g.coal)
            for node2 in inf_list:  # add results
                dirgraph.add_edge(node2, node[0], weight=inf_list[node2])
    return dirgraph


# Define SRIC influence on 'node'
def individual_sric(g, node, q, group_size):
    adj_links = g.in_edges(node, data=True)  # find all incoming edges to 'node'
    inf_list, nodes_id = dict(), dict()  # results of SRIC influence, nodes ID
    nodes_tuple, nodes_names = [], []  # adjacent nodes data (weight, SRIC influence, ID), nodes names
    s = 0
    for link in adj_links:
        nodes_names.append(link[0])
        nodes_id[link[0]] = len(nodes_tuple)
        w = link[2]['weight']
        nodes_tuple.append([w, 0, len(nodes_tuple)])  # generate list of neighbors
        s += w

    if len(nodes_tuple) > 0 and (s >= q or isclose(s, q)):  # list is not empty and affects 'node'
        nodes_names.append(node)
        nodes_tuple = sorted(nodes_tuple)
        partial_inf = define_sric(np.array(nodes_tuple, dtype='d'),
                                  q,
                                  min(group_size, len(nodes_tuple)),
                                  generate_sric_matrix(g.subgraph(nodes_names),
                                                       nodes_id, node,
                                                       g.nodes(data=True)[node]['indeg'])
                                  )  # calculate SRIC influence
        s = sum(partial_inf[:, 1])  # normalize SRIC influence
        for i in range(len(partial_inf)):
            if partial_inf[i, 1] > 0:
                inf_list[nodes_names[nodes_tuple[i][2]]] = partial_inf[i, 1]/s
    return inf_list


# Define LRIC direct influence on 'node'
def individual_lric(adj_links, quota, group_size):
    inf_list = dict()  # results of LRIC influence
    nodes_tuple, nodes_names = [], []  # adjacent nodes (weight, ID1, min influence, quota, status, ID2), nodes names
    s = 0
    if len(adj_links) > 0:
        for link in adj_links:
            min_w, max_w = link[2]['weight'], link[2]['weight']
            break
    for link in adj_links:  # generate list of neighbors
        w = link[2]['weight']
        if w >= quota:
            inf_list[link[0]] = 1
        else:
            min_w = min(min_w, w)
            max_w = max(max_w, w)
            nodes_names.append(link[0])
            nodes_tuple.append([w, len(nodes_tuple), quota - w, quota, 0, 0])
            s += w

    if len(nodes_tuple) > 0 and (s >= quota or isclose(s, quota)):   # list is not empty and affects node
        if isclose(s, quota):  # if total weight is equal to quota, then influence is proportional to links weights
            for inf in nodes_tuple:
                inf_list[nodes_names[inf[1]]] = inf[0]/quota
        elif s > quota and isclose(min_w, max_w):
            n = ceil(quota / max_w)
            for inf in nodes_tuple:
                inf_list[nodes_names[inf[1]]] = 1 / n
        else:
            nodes_tuple = np.asarray(sorted(nodes_tuple))
            nodes_tuple[:, 5] = range(len(nodes_tuple))  # generate ID2
            if isclose(nodes_tuple[0][0], nodes_tuple[-1][0]):  # check if all adjacent nodes have the same weight
                value = 1 / (ceil(nodes_tuple[0][3] / nodes_tuple[0][0]))  # calculate LRIC value
                partial_inf = zip([value] * len(nodes_tuple), nodes_tuple[:, 1])
            else:  # nodes weights are different
                partial_inf = []
                arr = find_lp(nodes_tuple, len(nodes_tuple) // 2, group_size - 1, dict())  # define LRIC for all nodes
                for elem in arr:
                    if not isclose(elem[4], -2):  # check if element is pivotal
                        partial_inf.append((elem[0] / (elem[0] + elem[3]), elem[1]))
            for inf in partial_inf:
                inf_list[nodes_names[int(inf[1])]] = inf[0]
    return inf_list
