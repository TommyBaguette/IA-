import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import osmnx as ox
import os
from matplotlib.patches import Patch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.legend_handler import HandlerBase

fig, ax = None, None
taxi_image = None

class HandlerImage(HandlerBase):
    def __init__(self, img_data, zoom=1):
        self.image_data = img_data
        self.zoom = zoom
        super().__init__()

    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        oi = OffsetImage(self.image_data, zoom=self.zoom)
        ab = AnnotationBbox(oi, (width / 2., height / 2.),
                            xycoords="data",
                            frameon=False,
                            pad=0,
                            annotation_clip=False)
        ab.set_transform(trans)
        return [ab]

def preparar_janela():
    global fig, ax, taxi_image
    plt.ion()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    plt.subplots_adjust(right=0.70) 

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
    handler_map = {}

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
        taxi_legend_artist = OffsetImage(taxi_image, zoom=1)
        legend_elements.append(taxi_legend_artist)
        handler_map[OffsetImage] = HandlerImage(taxi_image, zoom=0.5)
    else:
        legend_elements.append(Patch(facecolor='yellow', edgecolor='black', label='Táxis'))
        
  
    ax.legend(handles=legend_elements, 
              handler_map=handler_map,
              loc='lower left',       
              bbox_to_anchor=(1.02, 0.0), 
              fontsize=10, 
              framealpha=0.9,
              handletextpad=0.7)

def desenhar_frame_animado(ax, G, frota_taxis, artists_anteriores):

    if not plt.fignum_exists(fig.number):

        return [], False 


    novos_artists = [] 


    if artists_anteriores:

        for artist in artists_anteriores:

            artist.remove()


    if frota_taxis:

        try:

            texto_estado = "ESTADO DA FROTA:\n"

            texto_estado += f"{'ID':<4}  {'Auto(km)':<8}   {'Custo':<8}     {'CO2':<6}   {'Estado'}\n"

            texto_estado += "-"*48 + "\n"


            for t in frota_taxis:

                km_restantes = t.autonomia_atual / 1000.0

                estado_str = "Livre"

                if t.estado == "a_abastecer": estado_str = "A abastecer"

                elif t.estado == "sem_energia": estado_str = "MORTO"

                linha = f"{t.id:<4} {km_restantes:>7.1f}   {t.custo_total:>7.2f}€   {t.emissoes_CO2:>5.0f}kg      {estado_str}\n"

                texto_estado += linha

            text_artist = ax.text(1.02, 0.6, texto_estado, 
                                  transform=ax.transAxes, 
                                  fontsize=9, 
                                  family='monospace', 
                                  verticalalignment='center', 
                                  bbox=dict(boxstyle='round', facecolor='white', alpha=1.0, edgecolor='gray'))

            novos_artists.append(text_artist)


        except Exception:

            pass

        try:

            if taxi_image is not None:

                for t in frota_taxis:

                    if t.posicao_atual in G.nodes and t.estado != "sem_energia":

                        x = G.nodes[t.posicao_atual]['x']

                        y = G.nodes[t.posicao_atual]['y']

                        oi = OffsetImage(taxi_image, zoom=0.08)

                        ab = AnnotationBbox(oi, (x, y), xycoords='data', frameon=False, zorder=10)

                        ax.add_artist(ab)

                        novos_artists.append(ab)

            else:

                lons, lats = [], []

                for t in frota_taxis:

                    if t.posicao_atual in G.nodes and t.estado != "sem_energia":

                        lons.append(G.nodes[t.posicao_atual]['x'])

                        lats.append(G.nodes[t.posicao_atual]['y'])

                

                scatter = ax.scatter(lons, lats, c='yellow', s=120, 

                                     marker='s', edgecolors='black', linewidth=1, zorder=10)

                novos_artists.append(scatter)


        except Exception:

            pass

    

    plt.pause(0.05) 

    

    return novos_artists, True