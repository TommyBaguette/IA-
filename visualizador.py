import matplotlib.pyplot as plt
import osmnx as ox

fig, ax = None, None

def preparar_janela():
    global fig, ax
    plt.ion()
    fig, ax = plt.subplots(figsize=(15, 15))
    return fig, ax

def fechar_janela():
    plt.ioff()
    if fig:
        plt.close(fig)

def desenhar_frame(ax, G, pois_frota, frota_taxis, passo_atual, passos_totais):
    
    if not plt.fignum_exists(fig.number):
        return False
    
    ax.clear()

    # 1. Desenhar Mapa
    ox.plot_graph(G, ax=ax, node_size=0, edge_color='#2E86AB', 
                  edge_linewidth=0.8, edge_alpha=0.7, 
                  bgcolor='#F8F9FA', show=False, close=False)
    
    # 2. Desenhar POIs
    if pois_frota.get("bombas_gasolina"):
        lons = [p["longitude"] for p in pois_frota["bombas_gasolina"]]
        lats = [p["latitude"] for p in pois_frota["bombas_gasolina"]]
        ax.scatter(lons, lats, c='red', s=100, marker='o', zorder=5, label="Bombas")

    if pois_frota.get("carregadores_eletricos"):
        lons = [p["longitude"] for p in pois_frota["carregadores_eletricos"]]
        lats = [p["latitude"] for p in pois_frota["carregadores_eletricos"]]
        ax.scatter(lons, lats, c='green', s=100, marker='^', zorder=4, label="Carregadores")

    # 3. Desenhar Taxis
    if frota_taxis:
        try:
            taxis_lons = [G.nodes[t.posicao_atual]['x'] for t in frota_taxis]
            taxis_lats = [G.nodes[t.posicao_atual]['y'] for t in frota_taxis]
            ax.scatter(taxis_lons, taxis_lats, c='yellow', s=120, 
                       marker='s', edgecolors='black', linewidth=1, 
                       label='Taxis', zorder=10)
        except KeyError as e:
            # Este print é aceitável na View, pois é um erro de desenho
            print(f"Erro ao encontrar nó do táxi: {e}. O táxi pode ter uma posição inválida.")
    
    ax.set_axis_off()
    ax.set_title(f"Simulação TaxiGreen - Passo {passo_atual}/{passos_totais}", fontsize=16)
    
    plt.pause(0.1)
    return True