import heapq
from collections import deque
import utils as ut
import networkx as nx 

def obter_peso(G, u, v):
   
    try:
        
        dados = G[u][v][0]
        return dados.get('peso_dinamico', dados.get('length', 1))
    except (KeyError, IndexError, TypeError):
        return 1

def calcular_custo_caminho(G, path):
    custo = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        custo += obter_peso(G, u, v)
    return custo

def procura_DFS(G, start, finish):
    stack = [(start, [start])]
    visited = set()

    while stack:
        (vertex, path) = stack.pop()
        
        if vertex == finish:
            return path

        if vertex in visited:
            continue
        
        visited.add(vertex)

        for neighbor in G.neighbors(vertex):
            if neighbor not in visited:
               
                stack.append((neighbor, path + [neighbor]))
    
    return None

def procura_BFS(G, start, finish):

    queue = deque([start])
    visited = {start}
    parents = {start: None}

    while queue:
        current = queue.popleft()
        
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

    count = 0
    open_set = [(0, count, start)]
    
    g_score = {node: float('inf') for node in G.nodes}
    g_score[start] = 0
    
    parents = {}
    open_set_hash = {start}

    while open_set:
        _, _, current = heapq.heappop(open_set)
        
        if current in open_set_hash:
            open_set_hash.remove(current)

        if current == end:
            path = []
            while current in parents:
                path.insert(0, current)
                current = parents[current]
            path.insert(0, start)
            return path

        for vizinho in G.neighbors(current):
        
            peso = obter_peso(G, current, vizinho)
            tentative_g_score = g_score[current] + peso

            if tentative_g_score < g_score[vizinho]:
                parents[vizinho] = current
                g_score[vizinho] = tentative_g_score
                f_score = tentative_g_score + ut.heuristica(G, vizinho, end)
                
                if vizinho not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (f_score, count, vizinho))
                    open_set_hash.add(vizinho)
    return None

def procura_Greedy(G, start, end):

    count = 0
    priority_queue = [(ut.heuristica(G, start, end), count, start)]
    
    visited = set()
    parents = {}

    while priority_queue:
        _, _, current = heapq.heappop(priority_queue)

        if current == end:
            path = []
            while current in parents:
                path.insert(0, current)
                current = parents[current]
            path.insert(0, start)
            return path

        if current in visited:
            continue
        visited.add(current)

        for vizinho in G.neighbors(current):
            if vizinho not in visited and vizinho not in parents:
                parents[vizinho] = current
                count += 1
                h_score = ut.heuristica(G, vizinho, end)
                heapq.heappush(priority_queue, (h_score, count, vizinho))
    return None

def procura_Dijkstra(G, start, end):

    count = 0
    priority_queue = [(0, count, start)]
    
    min_dist = {node: float('inf') for node in G.nodes}
    min_dist[start] = 0
    
    parents = {}
    visited = set()

    while priority_queue:
        current_cost, _, current_node = heapq.heappop(priority_queue)

        if current_node == end:
            path = []
            while current_node in parents:
                path.insert(0, current_node)
                current_node = parents[current_node]
            path.insert(0, start)
            return path

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_cost > min_dist[current_node]:
            continue

        for vizinho in G.neighbors(current_node):

            weight = obter_peso(G, current_node, vizinho)
            new_cost = current_cost + weight

            if new_cost < min_dist[vizinho]:
                min_dist[vizinho] = new_cost
                parents[vizinho] = current_node
                count += 1
                heapq.heappush(priority_queue, (new_cost, count, vizinho))
    return None

def calcular_rota(nome_algoritmo, G, origem, destino):
    if nome_algoritmo == "dfs":
        return procura_DFS(G, origem, destino)
    elif nome_algoritmo == "bfs":
        return procura_BFS(G, origem, destino)
    elif nome_algoritmo == "astar":
        return procura_AStar(G, origem, destino)
    elif nome_algoritmo == "greedy":
        return procura_Greedy(G, origem, destino)
    else:
        return procura_Dijkstra(G, origem, destino)