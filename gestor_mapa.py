import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import json
import os
import random

def criar_mapa_base():
    """Baixa o Grafo + POIs apenas da Frota (bombas, carregadores)"""
    
    # Configurar
    ox.settings.log_console = True
    ox.settings.use_cache = True
    
    # Coordenadas de Matosinhos
    lat, lon = 41.1821, -8.6891
    dist = 5000
    
    print("=== SISTEMA DE MAPAS (BASE DA FROTA) ===\n")
    
    # 1. BUSCAR GRAFO DE ESTRADAS
    print("1. A descarregar grafo de estradas...")
    G = ox.graph_from_point((lat, lon), dist=dist, network_type="drive")
    print(f"   ✓ Grafo pronto: {len(G.nodes)} nós, {len(G.edges)} arestas")
    
    # 2. BUSCAR PONTOS DE INTERESSE (FROTA)
    print("\n2. A buscar pontos de interesse da frota...")
    
    # Bombas de gasolina
    bombas = ox.features_from_point(
        (lat, lon), 
        tags={"amenity": "fuel"}, 
        dist=dist
    )
    
    # Carregadores elétricos
    carregadores = ox.features_from_point(
        (lat, lon), 
        tags={"amenity": "charging_station"}, 
        dist=dist
    )
    
    print(f"   ✓ Bombas de gasolina: {len(bombas)}")
    print(f"   ✓ Carregadores elétricos: {len(carregadores)}")
    
    # 3. PROCESSAR E GUARDAR POIs EM JSON
    pois_data = {
        "bombas_gasolina": [],
        "carregadores_eletricos": []
    }
    
    # Processar bombas
    for idx, bomba in bombas.iterrows():
        if hasattr(bomba, 'geometry') and bomba.geometry is not None:
            coords = list(bomba.geometry.centroid.coords)[0]
            pois_data["bombas_gasolina"].append({
                "longitude": float(coords[0]),
                "latitude": float(coords[1]),
            })
    
    # Processar carregadores
    for idx, carregador in carregadores.iterrows():
        if hasattr(carregador, 'geometry') and carregador.geometry is not None:
            coords = list(carregador.geometry.centroid.coords)[0]
            pois_data["carregadores_eletricos"].append({
                "longitude": float(coords[0]),
                "latitude": float(coords[1]),
            })
    
    # Guardar JSON
    nome_ficheiro_pois = "pontos_interesse_matoshinhos.json"
    with open(nome_ficheiro_pois, "w", encoding="utf-8") as f:
        json.dump(pois_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ Pontos de interesse da frota guardados em {nome_ficheiro_pois}")
    
    # 4. GUARDAR GRAFO
    nome_ficheiro_grafo = "matosinhos_5km.graphml"
    ox.save_graphml(G, nome_ficheiro_grafo)
    
    print(f"   ✓ Grafo guardado em {nome_ficheiro_grafo}")
    
    print("\n SISTEMA BASE COMPLETO!")

def criar_zonas_recolha():
    """Baixa e guarda pontos de interesse de clientes (hotéis, hospitais, etc.)"""
    
    print("\n=== A CRIAR ZONAS DE RECOLHA DE CLIENTES ===")
    
    # Configurar
    ox.settings.log_console = True
    ox.settings.use_cache = True
    lat, lon = 41.1821, -8.6891
    dist = 5000
    
    # Tags que definem as "Zonas de Recolha"
    tags_a_buscar = {
        "hospitais": {"amenity": "hospital"},
        "hoteis": {"tourism": "hotel"},
        "estacoes_comboio_metro": {"railway": "station"},
        "estacoes_autocarro": {"amenity": "bus_station"},
        "pracas_taxis": {"amenity": "taxi"}
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
                    # Usar o .centroid para garantir que é um ponto
                    coords = list(feature.geometry.centroid.coords)[0] 
                    pontos_processados.append({
                        "longitude": float(coords[0]),
                        "latitude": float(coords[1]),
                    })
            
            zonas_data[nome_categoria] = pontos_processados
            print(f"   ✓ {nome_categoria.capitalize()}: {len(pontos_processados)} encontrados")
            
        except Exception as e:
            print(f"   ! Erro ao buscar {nome_categoria}: {e}")
            zonas_data[nome_categoria] = []

    # Guardar JSON
    nome_ficheiro = "zonas_recolha_matosinhos.json"
    with open(nome_ficheiro, "w", encoding="utf-8") as f:
        json.dump(zonas_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Zonas de recolha guardadas com sucesso em {nome_ficheiro}!")

def carregar_dados():
    """
    Função para carregar os dados base (Grafo e POIs da frota).
    """
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_data = json.load(f)
        
        print(" Dados base (Grafo e POIs da frota) carregados com sucesso!")
        return G, pois_data
    except FileNotFoundError:
        print(" Ficheiros não encontrados. Executa a opção 1 (Criar mapa base) primeiro.")
        return None, None

def verificar_ficheiros(lista_ficheiros):
    """Verifica se os ficheiros necessários existem"""
    faltam = []
    for ficheiro in lista_ficheiros:
        if not os.path.exists(ficheiro):
            faltam.append(ficheiro)
    return faltam

def visualizar_mapa_com_pois():
    
    print("A verificar ficheiros para visualização completa...")

    # --- 1. Carregar Grafo (Obrigatório) ---
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
    except FileNotFoundError:
        print(" Ficheiro 'matosinhos_5km.graphml' não encontrado.")
        print("   SOLUÇÃO: Executa a opção 1 (Criar mapa base) primeiro.")
        return

    # --- 2. Carregar POIs da Frota (Opcional) ---
    pois_data = {}
    try:
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_data = json.load(f)
        print("✓ POIs da frota carregados.")
    except FileNotFoundError:
        print("   - Aviso: 'pontos_interesse_matoshinhos.json' não encontrado. (Executa Opção 1)")

    # --- 3. Carregar e GENERALIZAR Zonas de Recolha (Opcional) ---
    lons_recolha_combinados = []
    lats_recolha_combinados = []
    try:
        with open("zonas_recolha_matosinhos.json", "r", encoding="utf-8") as f:
            zonas_data = json.load(f)
        
        # Juntar todos os pontos (hospitais, hoteis, etc.) num só grupo
        for categoria_de_pontos in zonas_data.values():
            for ponto in categoria_de_pontos:
                lons_recolha_combinados.append(ponto["longitude"])
                lats_recolha_combinados.append(ponto["latitude"])
        
        print(f"✓ Zonas de recolha carregadas e generalizadas ({len(lons_recolha_combinados)} pontos).")
        
    except FileNotFoundError:
        print("   - Aviso: 'zonas_recolha_matosinhos.json' não encontrado. (Executa Opção 2)")

    print("A gerar visualização...")
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plotar Estradas
    ox.plot_graph(
        G, ax=ax, node_size=0, edge_color='#2E86AB', edge_linewidth=0.8,
        edge_alpha=0.7, bgcolor='#F8F9FA', show=False, close=False
    )
    
    # --- Plotar POIs da Frota (Detalhado) ---
    # Bombas 
    if pois_data.get("bombas_gasolina"):
        lons = [p["longitude"] for p in pois_data["bombas_gasolina"]]
        lats = [p["latitude"] for p in pois_data["bombas_gasolina"]]
        ax.scatter(lons, lats, c='red', s=150, marker='o', edgecolors='white', 
                   label=f'Bombas ({len(lons)})', zorder=5)
    
    # Carregadores 
    if pois_data.get("carregadores_eletricos"):
        lons = [p["longitude"] for p in pois_data["carregadores_eletricos"]]
        lats = [p["latitude"] for p in pois_data["carregadores_eletricos"]]
        ax.scatter(lons, lats, c='green', s=150, marker='^', edgecolors='white',
                   label=f'Carregadores ({len(lons)})', zorder=5)

    # --- Plotar Zonas de Recolha (Generalizado) ---
    # Pontos de Recolha
    if lons_recolha_combinados:
        ax.scatter(lons_recolha_combinados, lats_recolha_combinados, 
                   c='#000000',
                   s=150, 
                   marker='o', 
                   label=f'Pontos de Recolha ({len(lons_recolha_combinados)})', 
                   zorder=3)

    # Configurações finais
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
    
    # 2. Gerar coordenadas aleatórias dentro desses limites
    random_lat = random.uniform(min_lat, max_lat)
    random_lon = random.uniform(min_lon, max_lon)
    
    # 3. Encontrar o nó da estrada mais próximo (o "snap" à rua)
    no_mais_proximo_id = ox.nearest_nodes(G, X=random_lon, Y=random_lat)
    
    # 4. Obter as coordenadas reais desse nó
    node_data = G.nodes[no_mais_proximo_id]
    
    coordenadas_pedido = {
        "id_no_origem": no_mais_proximo_id,
        "latitude": node_data['y'],
        "longitude": node_data['x'],
        "ponto_original_cliente": (random_lat, random_lon)
    }
    
    return coordenadas_pedido