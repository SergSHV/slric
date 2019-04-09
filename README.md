# SLRIC package  <img align="middle" src="https://www.hse.ru/data/2019/03/29/1187981536/slric.png" alt="drawing" width="40"/>

<p>SLRIC is a Python package for influence assessment in networks using short-range interaction centrality (SRIC) and long-range interaction centrality (LRIC) indices.</p>
<div>
<p>SRIC and LRIC indices take into account:</p>
<ul>
<li>Individual attributes of nodes: threshold of influence (quota), nodes size, etc.;</li>
<li>Possiblity of the group influence;</li>
<li>Indirect connections between nodes.</li>
</ul>
</div>
<b>Example:</b>
<div style="display: flex; justify-content: center;">
  <img src="https://www.hse.ru/data/2019/03/29/1187981382/graph.png" alt="SLRIC features" width="300"/>
<ul>
<li>Nodes 2 and 4 have different thresholds of influence (<i>q</i>);</li>
<li>Nodes 1 and 2 influence node 4 as a group. Even though node 3 is connected to node 4, it does not influence it directly as node 3 is not a pivotal member in any group;</li>
<li>Node 3 influences node 4 via node 2.</li>
</ul>
<p>Website: <a href="https://github.com/SergSHV/slric" rel="nofollow">https://github.com/SergSHV/slric</a>
<p>Authors: <a href="https://www.hse.ru/en/org/persons/140159" rel="nofollow">Fuad Aleskerov</a>, <a href="https://www.hse.ru/en/staff/natamesc" rel="nofollow">Natalia Meshcheryakova</a>, <a href="https://www.hse.ru/en/staff/Shv" rel="nofollow">Sergey Shvydun</a> (HSE University, ICS RAS)</div>

## Installation
Install the package from PyPI:

    $ pip install slric

You can also install the latest version from GitHub:

    $ pip install git+https://github.com/SergSHV/slric.git

## Load SLRIC package:


    >>> import slric


## SRIC/LRIC Calculation for Simple Example

Generate a network using NetworkX package 


    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_edge(1, 4, weight=7)
    >>> G.add_edge(2, 4, weight=5)
    >>> G.add_edge(3, 4, weight=2)
    >>> G.add_edge(3, 2, weight=6) 


**Case 1**
- *q*=60% of weighted in-degree (in percentage);
-  nodes have the same size (*size* = 1).

[//]: # (Case 1)



 
    >>> slric.sric(G, q=60, size=1) # SRIC 
    {1: 0.36363636363636365, 4: 0.0, 2: 0.09740259740259741, 3: 0.538961038961039}
    
    >>> slric.lric(G, q=60, size=1, models='max') # LRIC (Max) 
    {1: 0.27450980392156865, 4: 0.0, 2: 0.1470588235294118, 3: 0.5784313725490197}
    
    >>> slric.lric(G, q=60, size=1, models='maxmin') # LRIC (MaxMin)
    {1: 0.27450980392156865, 4: 0.0, 2: 0.1470588235294118, 3: 0.5784313725490197}
    
    >>> slric.lric(G, q=60, size=1, models='pagerank') # LRIC (PageRank)
    {1: 0.32165639923246203, 4: 0.0, 2: 0.18808528619697315, 3: 0.49025831457056473}
 
 
 **Case 2** 
- *q*=5 for each node (defined quota, *dq*);
- nodes have the same size (*size* = 1).

[//]: # (Case 2)
 
    
    >>> slric.sric(G, dq=5, size=1) # SRIC
    {1: 0.21153846153846154, 4: 0.0, 2: 0.28846153846153844, 3: 0.5}
    
    >>> slric.lric(G, dq=5, size=1, models='max') # LRIC (Max)
    {1: 0.25, 4: 0.0, 2: 0.25, 3: 0.5}


**Case 3** 
- *q*=5 for node 2, *q*=10 for node 4;
- nodes have the same size (*size* = 1).

[//]: # (Case 3)


    >>> d = dict()
    >>> d[2] = 5
    >>> d[4] = 10
    
    >>> slric.sric(G, dq=d, size=1) # SRIC
    {1: 0.2916666666666667, 4: 0.0, 2: 0.20833333333333337, 3: 0.5}
    
    >>> slric.lric(G, dq=d, size=1, models='max') # LRIC (Max)
    {1: 0.24137931034482757, 4: 0.0, 2: 0.17241379310344826, 3: 0.5862068965517241}


## Write LRIC results to file
    >>> from slric import lric, GraphQW
    >>> ranking, lric_graph = lric(G, q=60, size=1, models=['max', 'maxmin'], data=TRUE)
    >>> GraphQW.write_centrality(lric_graph, 'output.txt', separator=';', mode='w')


## Additional features
1) If nodes size (*size*) is not defined, then *size* = weighted out-degree;
2) Similarly to threshold of influence (*q*), nodes size can be of dict() type;
3) Maximal group size can be limited using '*group_size*' parameter (by default, *group_size*=4);
4) Maximal indirect influence limit can be defined using '*limpath*' parameter (by default, *limpath*=3);
5) If LRIC version (*models*) is not defined, then LRIC (Max) is calculated by default (*models='max'* ).

## License

BSD 3-Clause License

Copyright (c) 2019. Fuad Aleskerov, Natalia Meshcheryakova, Sergey Shvydun.

All rights reserved.
