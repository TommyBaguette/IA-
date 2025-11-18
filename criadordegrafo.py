import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import json
import os

def main():
    """SISTEMA COMPLETO - Grafo + POIs para táxis em Matosinhos"""
    
    # Configurar
    ox.settings.log_console = True
    ox.settings.use_cache = True
    
    # Coordenadas de Matosinhos
    lat, lon = 41.1821, -8.6891
    
    print("=== SISTEMA DE MAPAS PARA TÁXIS ===\n")
    
    # 1. BUSCAR GRAFO DE ESTRADAS
    print("1. A descarregar grafo de estradas...")
    G = ox.graph_from_point((lat, lon), dist=5000, network_type="drive")
    print(f"   ✓ Grafo pronto: {len(G.nodes)} nós, {len(G.edges)} arestas")
    
    # 2. BUSCAR PONTOS DE INTERESSE
    print("\n2. A buscar pontos de interesse...")
    
    # Bombas de gasolina
    bombas = ox.features_from_point(
        (lat, lon), 
        tags={"amenity": "fuel"}, 
        dist=5000
    )
    
    # Carregadores elétricos
    carregadores = ox.features_from_point(
        (lat, lon), 
        tags={"amenity": "charging_station"}, 
        dist=5000
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
    with open("pontos_interesse_matoshinhos.json", "w", encoding="utf-8") as f:
        json.dump(pois_data, f, ensure_ascii=False, indent=2)
    
    print("   ✓ Pontos de interesse guardados em JSON")
    
    # 4. VISUALIZAR TUDO JUNTO
    print("\n3. A gerar visualização...")
    
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plotar estradas (azul)
    ox.plot_graph(
        G,
        ax=ax,
        node_size=0,
        edge_color='#2E86AB',
        edge_linewidth=0.8,
        edge_alpha=0.7,
        bgcolor='#F8F9FA',
        show=False,
        close=False
    )
    
    # Bombas de gasolina
    if pois_data["bombas_gasolina"]:
        bombas_lons = [p["longitude"] for p in pois_data["bombas_gasolina"]]
        bombas_lats = [p["latitude"] for p in pois_data["bombas_gasolina"]]
        
        ax.scatter(
            bombas_lons, bombas_lats, 
            c='red', 
            s=150,
            marker='o', 
            edgecolors='white',
            linewidth=2,
            label=f'Bombas Gasolina ({len(bombas_lons)})',
            alpha=0.9,
            zorder=5
        )
    
    # Elétricos
    if pois_data["carregadores_eletricos"]:
        carg_lons = [p["longitude"] for p in pois_data["carregadores_eletricos"]]
        carg_lats = [p["latitude"] for p in pois_data["carregadores_eletricos"]]
        
        ax.scatter(
            carg_lons, carg_lats, 
            c='green', 
            s=150,
            marker='^',
            edgecolors='white',
            linewidth=2,
            label=f'Carregadores Elétricos ({len(carg_lons)})',
            alpha=0.9,
            zorder=5
        )
    
    # Personalizar
    ax.set_facecolor('white')
    
    plt.legend(loc='lower left', fontsize=12, framealpha=0.9)
    plt.axis('off')
    plt.tight_layout()
    
    # 5. GUARDAR GRAFO
    ox.save_graphml(G, "matosinhos_5km.graphml")
    
    print("\n SISTEMA COMPLETO!")
    print(f"Ficheiros criados:")
    print(f"   - matosinhos_5km.graphml (grafo das estradas)")
    print(f"   - pontos_interesse_matoshinhos.json (POIs)")
    print(f"   - Visualização no ecrã")
    
    plt.show()

def carregar_dados():
    """Função para carregar dados guardados (usar depois)"""
    try:
        G = ox.load_graphml("matosinhos_5km.graphml")
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_data = json.load(f)
        
        print("Dados carregados com sucesso!")
        return G, pois_data
    except FileNotFoundError:
        print("❌ Ficheiros não encontrados. Executa main() primeiro.")
        return None, None

def menu_principal():
    """Menu para escolher entre criar novo ou carregar existente"""
    
    print("\n=== MENU PRINCIPAL ===")
    print("1. Criar novo mapa (download)")
    print("2. Carregar mapa existente")
    print("3. Sair")
    
    escolha = input("\nEscolha (1-3): ").strip()
    
    if escolha == "1":
        main()
    elif escolha == "2":
        # Verifica se os ficheiros existem primeiro
        ficheiros_faltantes = verificar_ficheiros()
        if ficheiros_faltantes:
            print(f"❌ Ficheiros em falta: {', '.join(ficheiros_faltantes)}")
            print("💡 Executa a opção 1 primeiro para criar o mapa")
        else:
            carregar_e_visualizar_seguro()
    elif escolha == "3":
        print("👋 Até logo!")
    else:
        print("❌ Escolha inválida")

def verificar_ficheiros():
    """Verifica se os ficheiros necessários existem"""
    ficheiros_necessarios = [
        "matosinhos_5km.graphml",
        "pontos_interesse_matoshinhos.json"
    ]
    
    faltam = []
    for ficheiro in ficheiros_necessarios:
        if not os.path.exists(ficheiro):
            faltam.append(ficheiro)
    
    return faltam

def carregar_e_visualizar_seguro():
    """Carrega e mostra o mapa com verificações"""
    
    print("A verificar ficheiros...")
    
    # Verificar se os ficheiros existem
    ficheiros_faltantes = verificar_ficheiros()
    
    if ficheiros_faltantes:
        print("❌ Ficheiros em falta:")
        for ficheiro in ficheiros_faltantes:
            print(f"   - {ficheiro}")
        
        print("\n💡 SOLUÇÃO: Executa primeiro o comando:")
        print("   python sistema_taxis_matosinhos.py")
        return False
    
    try:
        print(" A carregar dados...")
        G = ox.load_graphml("matosinhos_5km.graphml")
        
        with open("pontos_interesse_matoshinhos.json", "r", encoding="utf-8") as f:
            pois_data = json.load(f)
        
        print("Mapa carregado com sucesso!")
        print(f"   Estradas: {len(G.nodes)} nós")
        print(f"   Bombas: {len(pois_data['bombas_gasolina'])}")
        print(f"   Carregadores: {len(pois_data['carregadores_eletricos'])}")
        
        print(" A gerar visualização...")
        fig, ax = plt.subplots(figsize=(15, 15))
        
        # Estradas
        ox.plot_graph(
            G, ax=ax,
            node_size=0,
            edge_color='#2E86AB',
            edge_linewidth=0.8,
            edge_alpha=0.7,
            bgcolor='#F8F9FA',
            show=False,
            close=False
        )
        
        # Bombas (vermelho)
        if pois_data["bombas_gasolina"]:
            bombas_lons = [p["longitude"] for p in pois_data["bombas_gasolina"]]
            bombas_lats = [p["latitude"] for p in pois_data["bombas_gasolina"]]
            ax.scatter(bombas_lons, bombas_lats, c='red', s=150, marker='o', 
                      edgecolors='white', linewidth=2, 
                      label=f'Bombas ({len(bombas_lons)})', alpha=0.9, zorder=5)
        
        # Carregadores (verde)
        if pois_data["carregadores_eletricos"]:
            carg_lons = [p["longitude"] for p in pois_data["carregadores_eletricos"]]
            carg_lats = [p["latitude"] for p in pois_data["carregadores_eletricos"]]
            ax.scatter(carg_lons, carg_lats, c='green', s=150, marker='^',
                      edgecolors='white', linewidth=2,
                      label=f'Carregadores ({len(carg_lons)})', alpha=0.9, zorder=5)
        
        # Configurações finais
        ax.set_facecolor('white')
        plt.legend(loc='lower left', fontsize=12)
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        print("💡 Tenta executar o sistema principal primeiro")
        return False


if __name__ == "__main__":
    menu_principal()
    
        
    
    # Para carregar depois, descomenta:
    # G, pois = carregar_dados()
    # print(f"Estradas: {len(G.nodes)} nós")
    # print(f"Bombas: {len(pois['bombas_gasolina'])}")
    # print(f"Carregadores: {len(pois['carregadores_eletricos'])}")