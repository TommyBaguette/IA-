import math
import networkx as nx

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula a distância em metros entre duas coordenadas (lat, lon)."""
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def heuristica(G, node_a, node_b):
    """Calcula a distância em linha reta entre dois nós do grafo."""
    try:
        lat1 = G.nodes[node_a]['y']
        lon1 = G.nodes[node_a]['x']
        lat2 = G.nodes[node_b]['y']
        lon2 = G.nodes[node_b]['x']
        return calcular_distancia_haversine(lat1, lon1, lat2, lon2)
    except KeyError:
        return float('inf')

def encontrar_poi_mais_proximo(G, posicao_atual, lista_pois):
    """
    Encontra o Ponto de Interesse (Bomba/Carregador) mais próximo.
    Movido do Motor para aqui por ser uma função utilitária de grafo.
    """
    melhor_distancia = float('inf')
    melhor_no = None

    for poi in lista_pois:
        no_destino = poi['id_no']
        try:
            dist = nx.shortest_path_length(G, posicao_atual, no_destino, weight='length')
            if dist < melhor_distancia:
                melhor_distancia = dist
                melhor_no = no_destino
        except nx.NetworkXNoPath:
            continue

    return melhor_no, melhor_distancia