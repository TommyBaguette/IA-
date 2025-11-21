import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt 
import json
import os
import random
import math

def criar_mapa_base():
    ox.settings.log_console = False
    ox.settings.use_cache = True
    
    lat, lon = 41.1821, -8.6891
    dist = 5000
    
    G = ox.graph_from_point((lat, lon), dist=dist, network_type="drive")
    G = ox.utils_graph.get_largest_component(G, strongly=True)

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
    

def criar_zonas_recolha():
    
    ox.settings.log_console = False
    ox.settings.use_cache = True
    lat, lon = 41.1821, -8.6891
    dist = 5000

    print("A carregar grafo de estradas...")
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
    except FileNotFoundError:
        return False
    
    tags_a_buscar = {
        "hospitais": {"amenity": "hospital"},
        "hoteis": {"tourism": "hotel"},
        "estacoes_comboio_metro": {"railway": "station"},
        "estacoes_autocarro": {"amenity": "bus_station"},
        "pracas_taxis": {"amenity": "taxi"},
        "restaurantes": {"amenity": "restaurant"},
        "supermercados": {"shop": "supermarket"}
    }
    
    zonas_data = {}
    print("A buscar zonas de recolha...")
    
    for nome_categoria, tags in tags_a_buscar.items():
        print(f"   A buscar: {nome_categoria}...")
        try:
            features = ox.features_from_point((lat, lon), tags=tags, dist=dist)
            pontos_processados = []
            for idx, feature in features.iterrows():
                if hasattr(feature, 'geometry') and feature.geometry is not None:
                    coords = list(feature.geometry.centroid.coords)[0]
                    try:
                        node_id = ox.nearest_nodes(G, X=coords[0], Y=coords[1])
                        node_data = G.nodes[node_id]
                        pontos_processados.append({
                            "id_no": node_id,
                            "longitude": float(node_data['x']),
                            "latitude": float(node_data['y']),
                        })
                    except:
                        pass
            
            zonas_data[nome_categoria] = pontos_processados
            print(f"   - {nome_categoria.capitalize()}: {len(pontos_processados)} encontrados")
        except Exception as e:
            zonas_data[nome_categoria] = []

    nome_ficheiro = "zonas_recolha_matosinhos.json"
    with open(nome_ficheiro, "w", encoding="utf-8") as f:
        json.dump(zonas_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n- Zonas de recolha guardadas com sucesso em {nome_ficheiro}!")
    return True

def carregar_dados():
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_data = json.load(f)
        return G, pois_data
    except FileNotFoundError:
        return None, None

def verificar_ficheiros(lista_ficheiros):
    faltam = []
    for ficheiro in lista_ficheiros:
        if not os.path.exists(ficheiro):
            faltam.append(ficheiro)
    return faltam

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def filtrar_pontos_com_hierarquia(pois_frota_data, zonas_data, distancia_minima):
    
    plotar_bombas = pois_frota_data.get("bombas_gasolina", [])
    plotar_carregadores = []
    plotar_recolha = []

    carregadores_brutos = pois_frota_data.get("carregadores_eletricos", [])
    for carregador in carregadores_brutos:
        demasiado_perto = False
        for bomba in plotar_bombas:
            dist = calcular_distancia(carregador["latitude"], carregador["longitude"], bomba["latitude"], bomba["longitude"])
            if dist < distancia_minima:
                demasiado_perto = True
                break
        if not demasiado_perto:
            plotar_carregadores.append(carregador)
    
    pontos_recolha_brutos = []
    for categoria in zonas_data.values():
        pontos_recolha_brutos.extend(categoria)
    
    pontos_prioritarios = plotar_bombas + plotar_carregadores
    ids_aceites = set()

    for ponto in pontos_recolha_brutos:
        if ponto["id_no"] in ids_aceites: continue
        
        demasiado_perto = False
        for poi in pontos_prioritarios:
            dist = calcular_distancia(ponto["latitude"], ponto["longitude"], poi["latitude"], poi["longitude"])
            if dist < distancia_minima:
                demasiado_perto = True
                break
        
        if demasiado_perto: continue

        for aceite in plotar_recolha:
            dist = calcular_distancia(ponto["latitude"], ponto["longitude"], aceite["latitude"], aceite["longitude"])
            if dist < distancia_minima:
                demasiado_perto = True
                break
        
        if not demasiado_perto:
            plotar_recolha.append(ponto)
            ids_aceites.add(ponto["id_no"])

    return plotar_bombas, plotar_carregadores, plotar_recolha

def visualizar_mapa_com_pois():
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
        with open("pontos_interesse_matoshinhos.json", "r") as f: pois_frota = json.load(f)
        with open("zonas_recolha_matosinhos.json", "r") as f: zonas = json.load(f)
    except:
        return

    bombas, carregadores, recolha = filtrar_pontos_com_hierarquia(pois_frota, zonas, 250)
    
    fig, ax = plt.subplots(figsize=(15, 15))
    ox.plot_graph(G, ax=ax, node_size=0, edge_color='#2E86AB', bgcolor='#F8F9FA', show=False)
    
    if bombas:
        ax.scatter([p["longitude"] for p in bombas], [p["latitude"] for p in bombas], c='red', s=100, zorder=5, label="Bombas")
    if carregadores:
        ax.scatter([p["longitude"] for p in carregadores], [p["latitude"] for p in carregadores], c='green', s=100, zorder=4, label="Carregadores")
    if recolha:
        ax.scatter([p["longitude"] for p in recolha], [p["latitude"] for p in recolha], c='black', s=100, zorder=3, label="Recolha")
        
    plt.legend()
    plt.show()

def gerar_pedido_local_aleatorio(G):
    lats = [data['y'] for node, data in G.nodes(data=True)]
    lons = [data['x'] for node, data in G.nodes(data=True)]
    rand_lat = random.uniform(min(lats), max(lats))
    rand_lon = random.uniform(min(lons), max(lons))
    no_id = ox.nearest_nodes(G, X=rand_lon, Y=rand_lat)
    node = G.nodes[no_id]
    return {"id_no_origem": no_id, "latitude": node['y'], "longitude": node['x']}