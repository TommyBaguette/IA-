import random
import variaveis as var
import utils as ut
from pedido import Pedido

class GeradorPedidos:
    def __init__(self, G):
        self.G = G
        self.todos_nos = list(self.G.nodes)
        self.pesos_nos = []
        self._calcular_pesos_hotspots()

    def _calcular_pesos_hotspots(self):
        for node in self.todos_nos:
            lat = self.G.nodes[node]['y']
            lon = self.G.nodes[node]['x']
            
            dist_ao_centro = ut.calcular_distancia_haversine(
                lat, lon, var.HOTSPOT_LAT, var.HOTSPOT_LON
            )
            
            if dist_ao_centro <= var.HOTSPOT_RAIO:
                self.pesos_nos.append(var.HOTSPOT_PESO)
            else:
                self.pesos_nos.append(1)

    def tentar_gerar(self, passo_atual, lista_pendentes):
        """Tenta gerar um pedido com base nas probabilidades e adiciona à lista."""
        if random.random() < var.PROB_GERAR_PEDIDO: 
        
            origem = random.choices(self.todos_nos, weights=self.pesos_nos, k=1)[0]
            destino = random.choice(self.todos_nos)
            
            origem_coords = (self.G.nodes[origem]['y'], self.G.nodes[origem]['x'])
            
            is_premium = random.random() < var.PROB_PREMIUM
            is_eco = random.random() < var.PROB_ECO_FRIENDLY
            
            novo_pedido = Pedido(
                id_pedido=f"P-{passo_atual}",
                origem=origem,
                destino=destino,
                origem_coords=origem_coords,
                premium=is_premium,
                eco=is_eco,
                tick_criacao=passo_atual
            )
            
            lista_pendentes.append(novo_pedido)
            return True
        return False