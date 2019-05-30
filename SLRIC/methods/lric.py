from cvxopt import matrix,  glpk
from math import floor, isclose
import numpy as np


# Calculate LRIC value for 'node'
def find_lp(arr, node, group_size, ex_list):
    if isclose(arr[node][4], -1) or isclose(arr[node][4], -2):  # check if LRIC for 'node' is already evaluated
        if node != len(arr) - 1:
            arr = find_lp(arr, next_element(arr, node), group_size, ex_list)  # calculate LRIC for the next node
    else:
        check = (0, 0)
        if node > 0:
            check = check_neighbors(node - 1, -1, -1, node, arr)  # check left
        if isclose(check[0], 0) and node < len(arr) - 1:
            check = check_neighbors(node + 1, len(arr), 1, node, arr)  # check right
        if isclose(check[0], 0):  # check if node is not considered
            if node in ex_list:  # check if there are exceptions for node
                ex = [True] * len(arr)
                for el in ex_list[node]:
                    ex[el] = False
                sub_arr = arr[(arr[:, 5] != node) & (arr[:, 4] != -2) & ex]  # generate list of other group members
            else:
                sub_arr = arr[(arr[:, 5] != node) & (arr[:, 4] != -2)]
            if len(sub_arr > 0):  # check if there are other members
                solution = ilp(sub_arr[:, 0], arr[node][2], arr[node][3], group_size)  # solve 0-1 problem
                if solution is None or isclose(sum(solution[:-1]),0):  # no solution found
                    if isclose(arr[node][4], 0):
                        for i in range(node + 1):
                            arr[i][4] = -2  # nodes are not pivotal
                    else:
                        arr[node][4] = -1  # node is considered
                else:
                    f = 0
                    for i in range(len(solution)-1):
                        f += solution[i]*sub_arr[i, 0]
                    if isclose(f, arr[node][3]) and isclose(arr[node][4], 0):  # solution - node is not pivotal
                        for i in range(node + 1):
                            arr[i][4] = -2  # nodes are not pivotal
                    else:
                        arr[node][4] = -1  # node is considered
                        arr[node][3] = f  # update node influence
                        for i in range(len(solution)-1):  # update influence for other group members
                            if isclose(solution[i], 1):
                                v = f + arr[node][0] - sub_arr[i][0]
                                if v < sub_arr[i][3]:
                                    j = int(sub_arr[i][5])
                                    arr[j][3] = v
                                    arr[j][4] = 1
                                    if j not in ex_list:  # add 'node' to exception list for j
                                        ex_list[j] = []
                                    ex_list[j].append(node)
            elif arr[node][4] == 0:
                arr[node][4] = -2  # node is not pivotal
        else:
            if isclose(check[0], -2):
                arr[node][4] = -2  # node is not pivotal
            else:
                arr[node][3] = check[1]  # node has the same influence as the other member
                arr[node][4] = -1
        if node != len(arr) - 1:
            arr = find_lp(arr, next_element(arr, node), group_size, ex_list)  # calculate LRIC for the next node
    return arr


# Check if influence of node with the same weight has been already evaluated
def check_neighbors(start, end, counter, ind, arr):
    check = (0, 0)  # tuple (node status, group weight)
    for i in range(start, end, counter):
        if isclose(arr[i][0], arr[ind][0]):  # check if node i has the same weight
            if arr[i][4] < -0.5:  # check if node i has been evaluated
                check = (arr[i][4], arr[i][3])
                break
        else:
            break
    return check


# Zero-One Linear Programming Solver
def ilp(weights, min_value, max_value, group_size):
    sum_w = sum(weights)
    if sum_w < min_value:
        return None
    else:
        weights = np.array(np.append(weights,[max_value]), dtype='d')
        c = matrix(weights, tc='d')
        G = matrix([list(-weights), list(weights), [1]*len(weights)], tc='d')
        h = matrix(np.array([-min_value, max_value, group_size], dtype='d'), tc='d')  # group is winning, node is pivotal, group size <= limit
        glpk.options['msg_lev'] = 'GLP_MSG_OFF'
        return glpk.ilp(c, G.T, h, B=set(range(len(weights))))[1]


# Find next element for LRIC calculation
def next_element(arr, node):
    if node > 0:
        if arr[node - 1][4] > -0.5:  # check if all nodes to the left are considered
            node = floor(node / 2)  # go left
        elif node < len(arr) - 1:
            node += 1  # go right
    else:
        node += 1  # go right
    return node
