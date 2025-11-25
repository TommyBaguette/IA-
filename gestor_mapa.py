import osmnx as ox
import networkx as nx
import json
import os
import math
import random
import matplotlib.pyplot as plt

def criar_mapa_base():
    ox.settings.log_console = False
    ox.settings.use_cache = True
    
    lat, lon = 41.1821, -8.6891
    dist = 5000
    
    G = ox.graph_from_point((lat, lon), dist=dist, network_type="drive")
    
    try:
        G = ox.truncate.largest_component(G, strongly=True)
    except AttributeError:
        try:
            G = ox.utils_graph.get_largest_component(G, strongly=True)
        except AttributeError:
             G = ox.get_largest_component(G, strongly=True)

    bombas = ox.features_from_point((lat, lon), tags={"amenity": "fuel"}, dist=dist)
    carregadores = ox.features_from_point((lat, lon), tags={"amenity": "charging_station"}, dist=dist)
    
    pois_data = {
        "bombas_gasolina": [],
        "carregadores_eletricos": []
    }
    
    for idx, bomba in bombas.iterrows():
        if hasattr(bomba, 'geometry') and bomba.geometry is not None:
            coords = list(bomba.geometry.centroid.coords)[0]
            try:
                node_id = ox.nearest_nodes(G, X=coords[0], Y=coords[1])
                node_data = G.nodes[node_id]
                pois_data["bombas_gasolina"].append({
                    "id_no": node_id,
                    "longitude": float(node_data['x']),
                    "latitude": float(node_data['y']),
                })
            except:
                pass
    
    for idx, carregador in carregadores.iterrows():
        if hasattr(carregador, 'geometry') and carregador.geometry is not None:
            coords = list(carregador.geometry.centroid.coords)[0]
            try:
                node_id = ox.nearest_nodes(G, X=coords[0], Y=coords[1])
                node_data = G.nodes[node_id]
                pois_data["carregadores_eletricos"].append({
                    "id_no": node_id,
                    "longitude": float(node_data['x']),
                    "latitude": float(node_data['y']),
                })
            except:
                pass
    
    nome_ficheiro_pois = "pontos_interesse_matoshinhos.json"
    with open(nome_ficheiro_pois, "w", encoding="utf-8") as f:
        json.dump(pois_data, f, ensure_ascii=False, indent=2)
    
    nome_ficheiro_grafo = "matosinhos_5km.graphml"
    ox.save_graphml(G, nome_ficheiro_grafo)

def carregar_dados():
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_data = json.load(f)
        return G, pois_data
    except FileNotFoundError:
        return None, None

def filtrar_pontos_com_hierarquia(pois_frota_data, distancia_minima):
    plotar_bombas = pois_frota_data.get("bombas_gasolina", [])
    plotar_carregadores = pois_frota_data.get("carregadores_eletricos", [])
    return plotar_bombas, plotar_carregadores, [] 

def visualizar_mapa_com_pois():
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_frota = json.load(f)
    except:
        return

    fig, ax = plt.subplots(figsize=(15, 15))
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color='#2E86AB', 
                  edge_linewidth=0.8, edge_alpha=0.7, 
                  bgcolor='#F8F9FA', show=False, close=False)
    
    bombas = pois_frota.get("bombas_gasolina", [])
    if bombas:
        lons = [p["longitude"] for p in bombas]
        lats = [p["latitude"] for p in bombas]
        ax.scatter(lons, lats, c='red', s=100, marker='o', zorder=5, label="Bombas")

    carregadores = pois_frota.get("carregadores_eletricos", [])
    if carregadores:
        lons = [p["longitude"] for p in carregadores]
        lats = [p["latitude"] for p in carregadores]
        ax.scatter(lons, lats, c='green', s=100, marker='^', zorder=4, label="Carregadores")
        
    plt.legend(loc='lower left')
    plt.axis('off')
    plt.show()