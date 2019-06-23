from math import isclose

# Binary search for element "<weight'
def search_low(left, right, tuples, weight):
    """
    :param left: search limit
    :param right: search limit
    :param tuples: array of elements
    :param weight: predefined value
    :return: index of array
    """
    v = 0
    if left == right:
        if tuples[left][1] >= weight:
            v = left - 1
            if left == 0 and weight < 0:
                v -= 1
        else:
            v = left
    else:
        mid = left + (right - left) // 2
        if tuples[mid][1] >= weight:
            v = search_low(left, mid, tuples, weight)  # search left
        else:
            v = search_low(mid + 1, right, tuples, weight)  # search right
    return v


# Binary search for element ">weight'
def search_high(left, right, tuples, weight):
    """
    :param left: search limit
    :param right: search limit
    :param tuples: array of elements
    :param weight: predefined value
    :return: index of array
    """
    v = 0
    if left == right:
        if tuples[left][1] > weight:
            v = left
        else:
            v = left + 1
    else:
        mid = left + (right - left) // 2
        if tuples[mid][1] > weight:
            v = search_high(left, mid, tuples, weight)  # search left
        else:
            v = search_high(mid + 1, right, tuples, weight)  # search right
    return v


# Binary search for element "=weight'
def search_value(left, right, ord_keys, d, weight):
    v = 0
    if left == right:
        if d[ord_keys[left]][0] != weight:
            v = left
        else:
            v = left + 1
    else:
        mid = left + (right - left) // 2
        if d[ord_keys[mid]][0] != weight:
            v = search_value(left, mid, ord_keys, d, weight)  # search left
        else:
            v = search_value(mid + 1, right, ord_keys, d, weight)  # search right
    return v


# Find max edge value in a graph
def max_edge(g, name, max_v):
    """
    :param g: input graph
    :param name: edge attribute name
    :param max_v: current maximum
    :return: max value
    """
    for edge in g.edges(data=True):
        if edge[2][name] > max_v:
            max_v = edge[2][name]
    return max_v


# Construct interval
def define_interval(weight, eps, method):
    """
    :param weight: element weight
    :param eps: measurement error
    :param method: method for interval construction (0 - error is absolute, 1 - error is relative)
    :return: interval value
    """
    if method == 0:
        return weight - eps, weight + eps
    else:
        return weight * (1 - eps), weight * (1 + eps)


# Construct interval of each element in array
def prepare_intervals(tuples, ord_keys, eps, method, count):
    """
    :param tuples: initial array
    :param ord_keys:  array keys
    :param eps: measurement error
    :param method: method for interval construction
    :param count: zero-elements
    :return: dict of intervals
    """
    d = dict()
    n = len(tuples) - 1
    if n >= 0:
        prev_high, prev_low = 0, 0
        for i in range(0, n + 1):
            min_v, max_v = define_interval(tuples[i][1], eps, method)
            if prev_high <= n:
                prev_high = search_high(prev_high, n, tuples, max_v)
            prev_low = search_low(max(0, prev_low), max(0, i - 1), tuples, min_v)
            d[tuples[i][0]] = [prev_low, prev_high]
    if count != 0:
        return d, search_value(0, n, ord_keys, d, -2)
    else:
        return d, 0


# Get list of ordered keys
def ordered_keys(tuples):
    """
    :param tuples: input array
    :return: list of keys
    """
    keys = list()
    for el in tuples:
        keys.append(el[0])
    return keys


#  Construct lower, equivalence, upper sets for a key
def construct_sets(key, ord_keys, interval, min_bord, n, dkeys):
    """
    :param key: input key (node name)
    :param ord_keys: ordered keys
    :param interval: interval values
    :param min_bord: non-zero index
    :param n: number of elements
    :param dkeys: elements not in ord_keys
    :return: lower, equivalence, upper sets
    """
    s = [set() for _ in range(3)]
    if key in interval:
        s[2] = set(ord_keys[interval[key][1]:n])
        s[1] |= set(ord_keys[max(0, interval[key][0] + 1):interval[key][1]])
        s[0] |= set(ord_keys[0:max(0, interval[key][0] + 1)])
    else:
        s[1] |= set(ord_keys[0:min_bord])
        s[2] |= set(ord_keys[min_bord:n])
    if len(dkeys) != 0:
        if key not in dkeys and not isclose(interval[key][0], -2):
            s[0] |= dkeys
        else:
            s[1] |= dkeys
    return s


# Ranking Distance
def rank_dist(r1, r2, eps, method):
    """
    :param r1: ranking 1 (dict)
    :param r2:  ranking 2 (dict)
    :param eps:  epsilon (measurement error)
    :param method: method for interval construction (o - absolute, 1 - relative)
    :return: ranking similarity
    """
    v = 0
    keys = set(r1.keys()) | set(r2.keys())  # keys list
    k1 = keys - set(r2.keys())  # elements of r1 that doesn't appear in r2
    k2 = keys - set(r1.keys())  # elements of r2 that doesn't appear in r1

    sort1, sort2 = list(r1.items()), list(r2.items())
    sort1.sort(key=lambda x: x[1])  # sort elements of r1
    sort2.sort(key=lambda x: x[1])  # sort elements of r2

    n1, n2 = len(sort1), len(sort2)
    ord_keys1, ord_keys2 = ordered_keys(sort1), ordered_keys(sort2)  # get ordered keys
    range1, min_bord1 = prepare_intervals(sort1, ord_keys1, eps, method, len(k2))  # construct intervals
    range2, min_bord2 = prepare_intervals(sort2, ord_keys2, eps, method, len(k1))  # construct intervals

    for key in keys:
        s1 = construct_sets(key, ord_keys1, range1, min_bord1, n1, k2)  # define sets for r1
        s2 = construct_sets(key, ord_keys2, range2, min_bord2, n2, k1)  # define sets for r2
        v += len(s1[2] & s2[0])
        v += len(s2[2] & s1[0])
        v += len(s1[1] ^ s2[1]) / 2
    v = v / (len(keys) * (len(keys) - 1))
    return v


# Topology Distance
def top_dist(g1, g2, name='weight', topology_type=0):
    """
    :param g1: graph 1
    :param g2:  graph 2
    :param name: compared edge attribute
    :param topology_type: topology distance normalization method
    :return: topology distance
    """
    max_v = max_edge(g1, name, max_edge(g2, name, 0))  # find max value in a graph
    v = 0
    nodes_list = set(g1.nodes()) | set(g2.nodes())  # define nodes list in g1 or g2
    degree1 = g1.degree(weight=name)  # define degree of g1
    degree2 = g2.degree(weight=name)  # define degree of g2
    for node in nodes_list:  # consider each node
        if node in g1.nodes() and node in g2.nodes():  # node appears in both graphs
            nodes1 = set(g1.neighbors(node))  # adjacent nodes in g1
            nodes2 = set(g2.neighbors(node)) - nodes1 # distinct adjacent nodes in g2
            for node2 in nodes1:
                if node2 in g2.neighbors(node):
                    v += abs(g1[node][node2][name]-g2[node][node2][name])
                else:
                    v += g1[node][node2][name]
            for node2 in nodes2:
                v += g2[node][node2][name]
        else:
            if node in g1.nodes():  # node appears only in g1
                v += degree1[node]
            else:
                v += degree2[node]  # node appears only in g2
    v /= max_v
    if topology_type == 0:
        return v/len(nodes_list)/len(nodes_list)
    else:
        num_edges = len(set(g1.edges()) | set(g2.edges()))
        return v/num_edges/num_edges
