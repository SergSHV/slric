from math import isclose


# Calculate SRIC influence through all winning groups of fixed size (nodes: "weight, inf, id", matr: SRIC intensities)
def define_sric(nodes, q, group_size, matr):
    coal = list(range(group_size))  # generate group
    n = len(nodes)  # number of adjacent nodes
    if group_size == 1:  # group contains only one node
        min_element = binary_search(0, n - 1, nodes[:, 0], q)  # find element for group to be winning
        while min_element != -1 and min_element < n:
            nodes[min_element, 1] += matr[min_element][min_element]
            min_element += 1
    else:  # group contains several nodes
        while coal[0] <= n - group_size:  # until all groups are not considered
            w = sum(nodes[coal[:-1], 0])
            if not isclose(w, q) and w < q:  # check if group can be pivotal
                min_value = q - w  # define minimal value for group to be winning
                min_element = binary_search(coal[-2] + 1, n - 1, nodes[:, 0], min_value)  # find required element
                if min_element != -1:  # check if such elements exist
                    while min_element < n and nodes[min_element, 0] < q:  # calculate SRIC for all group members
                        coal[-1] = min_element
                        for i in range(group_size):
                            if nodes[min_element, 0] - nodes[coal[i], 0] < min_value:  # check if node is pivotal
                                for j in range(group_size):
                                    nodes[coal[i], 1] += matr[nodes[coal[i], 2]].get(nodes[coal[j], 2], 0) / group_size
                        min_element += 1
                    while min_element < n:  # calculate SRIC for group member with weight >=quota
                        coal[-1] = min_element
                        for i in range(group_size):
                            nodes[min_element, 1] += matr[nodes[min_element, 2]].get(nodes[coal[i], 2], 0) / group_size
                        min_element += 1
            coal = next_coal(coal, n - 2, group_size - 2)  # generate next group
        nodes = define_sric(nodes, q, group_size - 1, matr)
    return nodes


# Calculation of direct and indirect intensities (p_ikj)
def generate_sric_matrix(g, nodes_names, ind, in_degree):
    sric_matr = dict()
    for node in nodes_names:
        sric_matr[nodes_names[node]] = dict()
    for edge in g.edges(data=True):
        if edge[0] != ind:
            if edge[1] != ind:  # indirect intensity
                w = g[edge[1]][ind]['weight']
                if edge[2]['weight'] > w:
                    sric_matr[nodes_names[edge[0]]][nodes_names[edge[1]]] = w / in_degree
                else:
                    sric_matr[nodes_names[edge[0]]][nodes_names[edge[1]]] = edge[2]['weight'] / in_degree
            else:  # direct intensity
                sric_matr[nodes_names[edge[0]]][nodes_names[edge[0]]] = edge[2]['weight'] / in_degree
    return sric_matr


# Define next possible group (lim: maximal element for j position in a group)
def next_coal(coal, lim, j):
    coal[j] += 1
    i = j
    while 0 <= i <= j:
        if coal[i] > lim - j + i:
            if i > 0:
                coal[i - 1] += 1
            i -= 1
        else:
            if i < j:
                coal[i + 1] = coal[i] + 1
            i += 1
    return coal


# Binary search of the first element '>=weight' in [left, right] segment
def binary_search(left, right, nodes_tuple, weight):
    v = 0
    if left == right:
        if nodes_tuple[left] >= weight:
            v = left
        else:
            v = -1  # element not found
    else:
        mid = left + (right - left) // 2
        if nodes_tuple[mid] >= weight:
            v = binary_search(left, mid, nodes_tuple, weight)  # search left
        else:
            v = binary_search(mid + 1, right, nodes_tuple, weight)  # search right
    return v
