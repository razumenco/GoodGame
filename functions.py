import base64
import random
from itertools import combinations, groupby
import networkx as nx
from networkx.generators.random_graphs import _random_subset





def CosarajuEndOfGame(nodes, edges):  # Алгоритм выявления компонент связанности Косарайю
    visited = {}
    for i in nodes:
        visited[i['data']['id']] = False
    components = []
    for node in nodes:
        if len(components) == 0:
            comp = dfs(node['data']['id'], edges, visited, [])
            components.append(comp)
        else:
            isIn = False
            for i in components:
                if node['data']['id'] in i:
                    isIn = True
            if isIn == False:
                comp = dfs(node['data']['id'], edges, visited, [])
                components.append(comp)
    if len(components) > 1:
        return True
    else:
        return False


def dfs(node, edges, visited, comp):  # Функция обхода графа в глубину
    visited[node] = True
    comp.append(node)
    adj = []
    for i in edges:
        if i['data']['source'] == node and i['data']['target'] != node:
            adj.append(i['data']['target'])
        elif i['data']['target'] == node and i['data']['source'] != node:
            adj.append(i['data']['source'])
    for w in adj:
        if not visited[w]:
            dfs(w, edges, visited, comp)
    return comp


def CSV_to_NX(content , node_count):  # Транслирует граф, записанный в CSV в граф NX

    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string).decode("utf-8").replace('\r', '').split('\n')
    g = nx.Graph()
    for i in decoded:
        node_count = node_count + 1
        line = i.split(';')
        for j in line:
            if line[0] != j:
                g.add_edge(int(line[0]), int(j), attr_dict=None)
    return g, node_count


def find_sharneers(edges):  # Поиск шарниров
    sharneers = []
    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge['data']['source'], edge['data']['target'])
    if not nx.is_connected(G):
        return []
    print(list(nx.articulation_points(G)))
    # if len(list(nx.all_node_cuts(G))[0]) >= 2:
    #     return []
    for i in list(nx.articulation_points(G)):
        sharneers.append(i)
    return sharneers


def check_ways(edges): # Функция подсчета путей в графе
    start = 0
    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge['data']['source'], edge['data']['target'])
    temp = nx.all_pairs_node_connectivity(G)
    for i in temp.keys():
        for k in temp[i]:
            start = start + temp[i][k]
    return start


def check_winning(edges):
    graph = nx.Graph()
    for edge in edges:
        print(edge)
        graph.add_edge(edge['data']['source'], edge['data']['target'])
    graphConnections = list(nx.connected_components(graph))
    intactness = 0
    print(len(graph.nodes()))
    for i in range(len(graphConnections)):
        print(intactness)
        nowGraph = nx.Graph()
        nowGraph.add_edges_from(graph.edges(graphConnections[i]))
        if len(nowGraph.nodes()) == 0:
            nowGraphNodes = 1
        else:
            nowGraphNodes = len(nowGraph.nodes())

        for j in range(i + 1, len(graphConnections)):
            currentGraph = nx.Graph()
            currentGraph.add_edges_from(graph.edges(graphConnections[j]))
            if len(currentGraph.nodes()) == 0:
                currentGraphNodes = 1
            else:
                currentGraphNodes = len(currentGraph.nodes())
            intactness += currentGraphNodes*nowGraphNodes*2
            print('fsdfsdfs'+str(currentGraphNodes))
        print(nowGraphNodes)
    return 1 - intactness/(len(graph.nodes()) ** 2)


def find_svyazn(edges):
    svyazn = {}
    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge['data']['source'], edge['data']['target'])
    for node in G.nodes():
        svyazn[node] = len(G.neighbors(node))
    return svyazn


def find_centr(edges):
    centr = {}
    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge['data']['source'], edge['data']['target'])
    centr = nx.betweenness_centrality(G)
    return centr


def find_clust(edges):
    clust = {}
    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge['data']['source'], edge['data']['target'])
    clust = nx.clustering(G)
    return clust