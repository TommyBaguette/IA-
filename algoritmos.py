import heapq
import utils as ut
import networkx as nx

def calcular_custo_caminho(G, path):
    custo = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        try:
            custo += G[u][v][0]['length']
        except:
            custo += 0
    return custo


def procura_DFS(G, start, finish):

    stack = [(start, [start])]
    visited = set()

    while stack:
        (vertex, path) = stack.pop()
        if vertex in visited: continue
        visited.add(vertex)

        if vertex == finish: return path

        for neighbor in G.neighbors(vertex):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))
    return None

def procura_BFS(G, start, finish):
    queue = [start]
    visited = {start}
    parents = {start: None}

    while queue:
        current = queue.pop(0)
        if current == finish: break

        for vizinho in G.neighbors(current):
            if vizinho not in visited:
                visited.add(vizinho)
                parents[vizinho] = current
                queue.append(vizinho)

    if finish not in parents: return None

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
            try: peso = G[current][vizinho][0]['length']
            except: peso = 1
            
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

def procura_Dijkstra(G, start, end):

    priority_queue = [(0, start)]
    min_dist = {node: float('inf') for node in G.nodes}
    min_dist[start] = 0
    parents = {}
    visited = set()

    while priority_queue:
        current_cost, current_node = heapq.heappop(priority_queue)

        if current_node == end:
            path = []
            while current_node in parents:
                path.insert(0, current_node)
                current_node = parents[current_node]
            path.insert(0, start)
            return path

        if current_node in visited: continue
        visited.add(current_node)

        for vizinho in G.neighbors(current_node):
            try: weight = G[current_node][vizinho][0]['length']
            except: weight = 1
            
            new_cost = current_cost + weight

            if new_cost < min_dist[vizinho]:
                min_dist[vizinho] = new_cost
                parents[vizinho] = current_node
                heapq.heappush(priority_queue, (new_cost, vizinho))
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