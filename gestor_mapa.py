import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import json
import os
import random
import math

def criar_mapa_base():
    ox.settings.log_console = True
    ox.settings.use_cache = True
    
    lat, lon = 41.1821, -8.6891
    dist = 5000
    
    print("=== SISTEMA DE MAPAS (BASE DA FROTA) ===\n")
    
    print("1. A descarregar grafo de estradas...")
    G = ox.graph_from_point((lat, lon), dist=dist, network_type="drive")
    print(f"   - Grafo pronto: {len(G.nodes)} nós, {len(G.edges)} arestas")
    
    print("\n2. A buscar pontos de interesse da frota...")
    bombas = ox.features_from_point((lat, lon), tags={"amenity": "fuel"}, dist=dist)
    carregadores = ox.features_from_point((lat, lon), tags={"amenity": "charging_station"}, dist=dist)
    
    print(f"   - Bombas de gasolina: {len(bombas)}")
    print(f"   - Carregadores elétricos: {len(carregadores)}")
    
    print("\n3. A ligar POIs aos nós da estrada...")
    pois_data = {
        "bombas_gasolina": [],
        "carregadores_eletricos": []
    }
    
    for idx, bomba in bombas.iterrows():
        if hasattr(bomba, 'geometry') and bomba.geometry is not None:
            coords = list(bomba.geometry.centroid.coords)[0]
            node_id = ox.nearest_nodes(G, X=coords[0], Y=coords[1])
            node_data = G.nodes[node_id]
            pois_data["bombas_gasolina"].append({
                "id_no": node_id,
                "longitude": float(node_data['x']),
                "latitude": float(node_data['y']),
            })
    
    for idx, carregador in carregadores.iterrows():
        if hasattr(carregador, 'geometry') and carregador.geometry is not None:
            coords = list(carregador.geometry.centroid.coords)[0]
            node_id = ox.nearest_nodes(G, X=coords[0], Y=coords[1])
            node_data = G.nodes[node_id]
            pois_data["carregadores_eletricos"].append({
                "id_no": node_id,
                "longitude": float(node_data['x']),
                "latitude": float(node_data['y']),
            })
    
    nome_ficheiro_pois = "pontos_interesse_matoshinhos.json"
    with open(nome_ficheiro_pois, "w", encoding="utf-8") as f:
        json.dump(pois_data, f, ensure_ascii=False, indent=2)
    
    print(f"   - Pontos de interesse da frota guardados em {nome_ficheiro_pois}")
    
    nome_ficheiro_grafo = "matosinhos_5km.graphml"
    ox.save_graphml(G, nome_ficheiro_grafo)
    
    print(f"   - Grafo guardado em {nome_ficheiro_grafo}")
    
    print("\n SISTEMA BASE COMPLETO!")

def criar_zonas_recolha():
    print("\n=== A CRIAR ZONAS DE RECOLHA DE CLIENTES ===")
    
    ox.settings.log_console = True
    ox.settings.use_cache = True
    lat, lon = 41.1821, -8.6891
    dist = 5000

    print("A carregar grafo de estradas (necessário para ligar os pontos)...")
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
    except FileNotFoundError:
        print("- ERRO: Ficheiro 'matosinhos_5km.graphml' não encontrado.")
        print("  SOLUÇÃO: Executa a opção 1 (Criar mapa base) primeiro.")
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
                    node_id = ox.nearest_nodes(G, X=coords[0], Y=coords[1])
                    node_data = G.nodes[node_id]
                    pontos_processados.append({
                        "id_no": node_id,
                        "longitude": float(node_data['x']),
                        "latitude": float(node_data['y']),
                    })
            
            zonas_data[nome_categoria] = pontos_processados
            print(f"   - {nome_categoria.capitalize()}: {len(pontos_processados)} encontrados")
            
        except Exception as e:
            print(f"   ! Erro ao buscar {nome_categoria}: {e}")
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
        
        print("- Dados base (Grafo e POIs da frota) carregados com sucesso!")
        return G, pois_data
    except FileNotFoundError:
        print("- Ficheiros não encontrados. Executa a opção 1 (Criar mapa base) primeiro.")
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
    
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def visualizar_mapa_com_pois():
    print("A verificar ficheiros para visualização completa...")
    DISTANCIA_MINIMA_METROS = 250

    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
    except FileNotFoundError:
        print("- Ficheiro 'matosinhos_5km.graphml' não encontrado.")
        print("  SOLUÇÃO: Executa a opção 1 (Criar mapa base) primeiro.")
        return

    pois_frota_data = {}
    try:
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_frota_data = json.load(f)
        print("- POIs da frota carregados.")
    except FileNotFoundError:
        print("  - Aviso: 'pontos_interesse_matoshinhos.json' não encontrado. (Executa Opção 1)")

    pontos_recolha_brutos = []
    try:
        with open("zonas_recolha_matosinhos.json", "r", encoding="utf-8") as f:
            zonas_data = json.load(f)
        
        for categoria_de_pontos in zonas_data.values():
            pontos_recolha_brutos.extend(categoria_de_pontos)
        
        print(f"- Zonas de recolha carregadas ({len(pontos_recolha_brutos)} pontos brutos).")
        
    except FileNotFoundError:
        print("  - Aviso: 'zonas_recolha_matosinhos.json' não encontrado. (Executa Opção 2)")

    print(f"A aplicar filtragem hierárquica com distância de {DISTANCIA_MINIMA_METROS}m...")

    plotar_bombas = []
    plotar_carregadores = []
    plotar_recolha = []

    plotar_bombas = pois_frota_data.get("bombas_gasolina", [])
    print(f"  - Prioridade 1 (Bombas): {len(plotar_bombas)} pontos aceites.")

    carregadores_brutos = pois_frota_data.get("carregadores_eletricos", [])
    for carregador in carregadores_brutos:
        demasiado_perto = False
        lon_novo, lat_novo = carregador["longitude"], carregador["latitude"]
        
        for bomba in plotar_bombas:
            dist = calcular_distancia(lat_novo, lon_novo, bomba["latitude"], bomba["longitude"])
            if dist < DISTANCIA_MINIMA_METROS:
                demasiado_perto = True
                break
        
        if not demasiado_perto:
            plotar_carregadores.append(carregador)
    
    print(f"  - Prioridade 2 (Carregadores): {len(plotar_carregadores)} pontos aceites (de {len(carregadores_brutos)}).")

    pontos_prioritarios = plotar_bombas + plotar_carregadores
    ids_de_recolha_aceites = set()

    for ponto_novo in pontos_recolha_brutos:
        demasiado_perto = False
        
        if ponto_novo["id_no"] in ids_de_recolha_aceites:
            continue
        
        lon_novo, lat_novo = ponto_novo["longitude"], ponto_novo["latitude"]

        for poi in pontos_prioritarios:
            dist = calcular_distancia(lat_novo, lon_novo, poi["latitude"], poi["longitude"])
            if dist < DISTANCIA_MINIMA_METROS:
                demasiado_perto = True
                break
        
        if demasiado_perto:
            continue

        for ponto_aceite in plotar_recolha:
            dist = calcular_distancia(lat_novo, lon_novo, ponto_aceite["latitude"], ponto_aceite["longitude"])
            if dist < DISTANCIA_MINIMA_METROS:
                demasiado_perto = True
                break

        if not demasiado_perto:
            plotar_recolha.append(ponto_novo)
            ids_de_recolha_aceites.add(ponto_novo["id_no"])

    print(f"  - Prioridade 3 (Recolha): {len(plotar_recolha)} pontos aceites (de {len(pontos_recolha_brutos)}).")

    print("A gerar visualização...")
    fig, ax = plt.subplots(figsize=(15, 15))
    
    ox.plot_graph(
        G, ax=ax, node_size=0, edge_color='#2E86AB', edge_linewidth=0.8,
        edge_alpha=0.7, bgcolor='#F8F9FA', show=False, close=False
    )
    
    if plotar_bombas:
        lons = [p["longitude"] for p in plotar_bombas]
        lats = [p["latitude"] for p in plotar_bombas]
        ax.scatter(lons, lats, c='red', s=150, marker='o', edgecolors='white', 
                   label=f'Bombas ({len(lons)})', zorder=5)
    
    if plotar_carregadores:
        lons = [p["longitude"] for p in plotar_carregadores]
        lats = [p["latitude"] for p in plotar_carregadores]
        ax.scatter(lons, lats, c='green', s=150, marker='^', edgecolors='white',
                   label=f'Carregadores ({len(lons)})', zorder=4)

    if plotar_recolha:
        lons = [p["longitude"] for p in plotar_recolha]
        lats = [p["latitude"] for p in plotar_recolha]
        ax.scatter(lons, lats, 
                   c='black', 
                   s=100, 
                   marker='o', 
                   edgecolors='white',
                   linewidth=1,
                   label=f'Pontos de Recolha ({len(lons)})', 
                   zorder=3)

    ax.set_facecolor('white')
    plt.legend(loc='lower left', fontsize=12, framealpha=0.9)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def gerar_pedido_local_aleatorio(G):
    lats = [data['y'] for node, data in G.nodes(data=True)]
    lons = [data['x'] for node, data in G.nodes(data=True)]
    
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    random_lat = random.uniform(min_lat, max_lat)
    random_lon = random.uniform(min_lon, max_lon)
    
    no_mais_proximo_id = ox.nearest_nodes(G, X=random_lon, Y=random_lat)
    
    node_data = G.nodes[no_mais_proximo_id]
    
    coordenadas_pedido = {
        "id_no_origem": no_mais_proximo_id,
        "latitude": node_data['y'],
        "longitude": node_data['x'],
        "ponto_original_cliente": (random_lat, random_lon)
    }
    
    return coordenadas_pedido