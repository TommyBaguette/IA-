import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import osmnx as ox
import os
from matplotlib.patches import Patch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

fig, ax = None, None
taxi_image = None

def preparar_janela():
    global fig, ax, taxi_image
    plt.ion()
    fig, ax = plt.subplots(figsize=(15, 15))

    image_path = os.path.join(os.path.dirname(__file__), "taxi_icon.png")
    if not os.path.exists(image_path):
        image_path = "taxi_icon.png" 
    
    try:
        taxi_image = mpimg.imread(image_path)
    except (FileNotFoundError, Exception):
        taxi_image = None

    return fig, ax

def fechar_janela():
    plt.ioff()
    if fig:
        plt.close(fig)

def desenhar_fundo_mapa(ax, G, plotar_bombas, plotar_carregadores, plotar_recolha):
    ox.plot_graph(G, ax=ax, node_size=0, edge_color='#2E86AB', 
                  edge_linewidth=0.8, edge_alpha=0.7, 
                  bgcolor='#F8F9FA', show=False, close=False)
    
    legend_elements = []

    if plotar_bombas:
        lons = [p["longitude"] for p in plotar_bombas]
        lats = [p["latitude"] for p in plotar_bombas]
        ax.scatter(lons, lats, c='red', s=100, marker='o', zorder=5)
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                          markerfacecolor='red', markersize=10, 
                                          label=f'Bombas ({len(lons)})'))

    if plotar_carregadores:
        lons = [p["longitude"] for p in plotar_carregadores]
        lats = [p["latitude"] for p in plotar_carregadores]
        ax.scatter(lons, lats, c='green', s=100, marker='^', zorder=4)
        legend_elements.append(plt.Line2D([0], [0], marker='^', color='w', 
                                          markerfacecolor='green', markersize=10, 
                                          label=f'Carregadores ({len(lons)})'))
    
    if plotar_recolha:
        lons = [p["longitude"] for p in plotar_recolha]
        lats = [p["latitude"]for p in plotar_recolha]
        ax.scatter(lons, lats, 
                   c='black', 
                   s=100, 
                   marker='o', 
                   edgecolors='white',
                   linewidth=1,
                   zorder=3)
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                          markerfacecolor='black', markeredgecolor='white',
                                          markersize=10, label=f'Pontos de Recolha ({len(lons)})'))
    
    ax.set_axis_off()
    
    if taxi_image is not None:
        legend_elements.append(Patch(facecolor='yellow', edgecolor='black', label='Táxis'))
    else:
        legend_elements.append(plt.Line2D([0], [0], marker='s', color='w', 
                                          markerfacecolor='yellow', markeredgecolor='black',
                                          markersize=10, label='Táxis'))
        
    ax.legend(handles=legend_elements, loc='lower left', fontsize=12, framealpha=0.9)


def desenhar_frame_animado(ax, G, frota_taxis, artist_anterior):
    
    if not plt.fignum_exists(fig.number):
        return None, False 

    if artist_anterior:
        if isinstance(artist_anterior, list):
            for ab in artist_anterior:
                ab.remove()
        else:
            artist_anterior.remove()

    novo_artist = None
    if frota_taxis:
        try:
            if taxi_image is not None:
                new_artists_list = []
                for t in frota_taxis:
                    x = G.nodes[t.posicao_atual]['x']
                    y = G.nodes[t.posicao_atual]['y']
                    oi = OffsetImage(taxi_image, zoom=0.075)
                    ab = AnnotationBbox(oi, (x, y), xycoords='data', frameon=False, zorder=10)
                    ax.add_artist(ab)
                    new_artists_list.append(ab)
                novo_artist = new_artists_list
                
            else:
                taxis_lons = [G.nodes[t.posicao_atual]['x'] for t in frota_taxis]
                taxis_lats = [G.nodes[t.posicao_atual]['y'] for t in frota_taxis]
                novo_artist = ax.scatter(taxis_lons, taxis_lats, c='yellow', s=120, 
                                         marker='s', edgecolors='black', linewidth=1, 
                                         zorder=10)
        except KeyError:
            pass
    
    plt.pause(0.5) 
    
    return novo_artist, True