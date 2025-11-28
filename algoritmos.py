import math
import algoritmos as pf
import utils as ut


def calcular_custo_caminho(G, path):
    custo = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        
        try:
            custo += G[u][v][0]['length']
        except:
            custo += 0
    return custo


def procura_DFS(G, start, finish, path=None, visited=None):
    if path is None: path = []
    if visited is None: visited = set()

    visited.add(start)
    path.append(start)

    if start == finish:
        return list(path) 

    for vizinho in G.neighbors(start):
        if vizinho not in visited:
            resultado = procura_DFS(G, vizinho, finish, path, visited)
            if resultado is not None:
                return resultado
    
    path.pop()
    return None

def procura_BFS(G, start, finish):
    queue = [start]
    visited = {start}
    parents = {start: None}

    while queue:
        current = queue.pop(0)

        if current == finish:
            break

        for vizinho in G.neighbors(current):
            if vizinho not in visited:
                visited.add(vizinho)
                parents[vizinho] = current
                queue.append(vizinho)

    if finish not in parents:
        return None

    path = []
    curr = finish
    while curr is not None:
        path.insert(0, curr)
        curr = parents[curr]
    
    return path

def procura_AStar(G, start, end):

    open_set = {start}
    
    g_score = {node: float('inf') for node in G.nodes}
    g_score[start] = 0
    
    f_score = {node: float('inf') for node in G.nodes}
    f_score[start] = ut.heuristica(G, start, end)
    
    parents = {}

    while open_set:
        current = min(open_set, key=lambda n: f_score[n])

        if current == end:
            path = []
            while current in parents:
                path.insert(0, current)
                current = parents[current]
            path.insert(0, start)
            return path

        open_set.remove(current)

        for vizinho in G.neighbors(current):

            peso = G[current][vizinho][0]['length']
            tentative_g_score = g_score[current] + peso

            if tentative_g_score < g_score[vizinho]:
                
                parents[vizinho] = current
                g_score[vizinho] = tentative_g_score
                f_score[vizinho] = g_score[vizinho] + ut.heuristica(G, vizinho, end)
                open_set.add(vizinho)

    return None

def procura_Greedy(G, start, end):
    open_list = {start}
    closed_list = set()
    parents = {}

    while open_list:
        n = min(open_list, key=lambda x: ut.heuristica(G, x, end))

        if n == end:
            path = []
            while n in parents:
                path.insert(0, n)
                n = parents[n]
            path.insert(0, start)
            return path

        open_list.remove(n)
        closed_list.add(n)

        for vizinho in G.neighbors(n):
            if vizinho not in open_list and vizinho not in closed_list:
                open_list.add(vizinho)
                parents[vizinho] = n

    return None