import math

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