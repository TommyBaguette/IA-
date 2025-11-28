import random
import networkx as nx
import json
import os
import math
import algoritmos as pf  
from taxi import Taxi
from pedido import Pedido
import utils as ut


class MotorSimulacao:
    def __init__(self, G, pois_frota_data, algoritmo="dijkstra"):
        self.G = G
        self.frota_taxis = []
        self.passo_atual = 0
        self.FATOR_CONSUMO = 1.0
        self.pois_frota = pois_frota_data
        self.pedidos_pendentes = []
        self.pedidos_completados = 0
        self.todos_nos = list(self.G.nodes)
        self.algoritmo_escolha = algoritmo  

    def criar_frota(self, config_file="frota.json"):
        if not os.path.exists(config_file): 
            if os.path.exists("frota.json"): config_file = "frota.json"
            else: return False, f"Ficheiro '{config_file}' nao encontrado."
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config_frota = json.load(f)

        for i, config_taxi in enumerate(config_frota):
            ponto_inicial = random.choice(self.todos_nos)
            novo_taxi = Taxi(
                id=config_taxi["id"],
                no_inicial=ponto_inicial,
                tipo_motor=config_taxi["tipo_motor"],
                capacidade=config_taxi["capacidade"],
                autonomia_max=config_taxi["autonomia_max"]
            )
            self.frota_taxis.append(novo_taxi)
        
        return True, ""

    def encontrar_caminho(self, origem, destino):
        caminho = None
        distancia = float('inf')

        try:
            if self.algoritmo_escolha == "dfs":
                caminho = pf.procura_DFS(self.G, origem, destino)
            elif self.algoritmo_escolha == "bfs":
                caminho = pf.procura_BFS(self.G, origem, destino)
            elif self.algoritmo_escolha == "astar":
                caminho = pf.procura_AStar(self.G, origem, destino)
            elif self.algoritmo_escolha == "greedy":
                caminho = pf.procura_Greedy(self.G, origem, destino)
            else:
                
                caminho = nx.dijkstra_path(self.G, origem, destino, weight='length')
            
            if caminho:
                
                if self.algoritmo_escolha == "dijkstra":
                    distancia = nx.path_weight(self.G, caminho, weight='length')
                else:
                    distancia = pf.calcular_custo_caminho(self.G, caminho)
                return caminho, distancia
                
        except Exception:
            return None, float('inf')
            
        return None, float('inf')

    def encontrar_poi_mais_proximo(self, taxi):
        if taxi.tipo_motor == 'eletrico':
            lista_pois = self.pois_frota.get('carregadores_eletricos', [])
        else:
            lista_pois = self.pois_frota.get('bombas_gasolina', [])
        
        melhor_distancia = float('inf')
        melhor_no = None

        for poi in lista_pois:
            no_destino = poi['id_no']
            try:
                dist = nx.shortest_path_length(self.G, taxi.posicao_atual, no_destino, weight='length')
                if dist < melhor_distancia:
                    melhor_distancia = dist
                    melhor_no = no_destino
            except nx.NetworkXNoPath:
                continue

        return melhor_no, melhor_distancia

    def gerar_novos_pedidos(self):
        if random.random() < 0.35: 
            origem = random.choice(self.todos_nos)
            destino = random.choice(self.todos_nos)
            origem_coords = (self.G.nodes[origem]['y'], self.G.nodes[origem]['x'])
            
            novo_pedido = Pedido(
                id_pedido=f"P-{self.passo_atual}",
                origem=origem,
                destino=destino,
                origem_coords=origem_coords
            )
            self.pedidos_pendentes.append(novo_pedido)

    def alocar_pedidos(self):

        for pedido in self.pedidos_pendentes:
            if pedido.estado != "pendente": continue

            candidatos = []
            dist_viagem_estimada = ut.heuristica(self.G, pedido.origem, pedido.destino)

            for taxi in self.frota_taxis:
                if taxi.estado == "livre":
        
                    margem_reserva_taxi = taxi.autonomia_maxima * 0.25
                    if taxi.autonomia_atual < margem_reserva_taxi:
                        continue 

                    dist_h = ut.heuristica(self.G, taxi.posicao_atual, pedido.origem)
                    candidatos.append((dist_h, taxi))

            if not candidatos: continue

            candidatos.sort(key=lambda x: x[0])
            top_candidatos = candidatos[:3] 

            melhor_taxi = None
            menor_custo_real = float('inf')

            for dist_h, taxi in top_candidatos:
                
                try:
                    dist_real_ate_pedido = nx.shortest_path_length(
                        self.G, taxi.posicao_atual, pedido.origem, weight='length'
                    )
                except nx.NetworkXNoPath:
                    continue
                
                custo_viagem_estimado = (dist_viagem_estimada * self.FATOR_CONSUMO) * 1.3
                custo_buscar = dist_real_ate_pedido * self.FATOR_CONSUMO
                custo_total = custo_buscar + custo_viagem_estimado
                
                margem = taxi.autonomia_maxima * 0.25

                if dist_real_ate_pedido < menor_custo_real and taxi.autonomia_atual > (custo_total + margem):
                    menor_custo_real = dist_real_ate_pedido
                    melhor_taxi = taxi
            
            if melhor_taxi:
        
                caminho, _ = self.encontrar_caminho(melhor_taxi.posicao_atual, pedido.origem)
                if caminho:
                    if len(caminho) > 0 and caminho[0] == melhor_taxi.posicao_atual:
                        caminho.pop(0)
                        
                    melhor_taxi.estado = "a_recolher"
                    melhor_taxi.rota_atual = caminho
                    melhor_taxi.objetivo_atual = pedido.origem
                    melhor_taxi.destino_passageiro = pedido.destino
                    melhor_taxi.pedido_atual = pedido 
                    pedido.estado = "atribuido"

    def verificar_e_atribuir_abastecimento(self):
        for taxi in self.frota_taxis:
            if taxi.estado != 'livre' or taxi.autonomia_atual <= 0:
                continue

            threshold = taxi.autonomia_maxima * 0.25 
            if taxi.autonomia_atual <= threshold:
                destino_abastecimento, dist_metros = self.encontrar_poi_mais_proximo(taxi)
                if destino_abastecimento is None: continue

                custo_real = dist_metros * self.FATOR_CONSUMO
                if (custo_real * 1.10) < taxi.autonomia_atual:
                    caminho, _ = self.encontrar_caminho(taxi.posicao_atual, destino_abastecimento)
                    if caminho:
                        if len(caminho) > 0 and caminho[0] == taxi.posicao_atual:
                            caminho.pop(0)
                        taxi.estado = 'a_abastecer' 
                        taxi.objetivo_atual = destino_abastecimento
                        taxi.rota_atual = caminho

    def executar_passo(self):
        self.gerar_novos_pedidos()
        self.alocar_pedidos()
        self.verificar_e_atribuir_abastecimento()

        for taxi in self.frota_taxis:
            if taxi.estado == "sem_energia": continue

            if taxi.posicao_atual == taxi.objetivo_atual:
                
                if taxi.estado == "a_abastecer":
                
                    taxi.ticks_a_carregar += 1 
                    
                    if taxi.carregar():
                        
                        taxi.estado = "livre"
                        taxi.objetivo_atual = None

                    continue 
                
                elif taxi.estado == "a_recolher":
                    if taxi.pedido_atual in self.pedidos_pendentes:
                        self.pedidos_pendentes.remove(taxi.pedido_atual)
                    
                    rota_destino, _ = self.encontrar_caminho(taxi.posicao_atual, taxi.destino_passageiro)
                    if rota_destino:
                        if len(rota_destino) > 0 and rota_destino[0] == taxi.posicao_atual:
                            rota_destino.pop(0)
                        
                        taxi.estado = "ocupado"
                        taxi.rota_atual = rota_destino
                        taxi.objetivo_atual = taxi.destino_passageiro
                    else:
                        taxi.estado = "livre"
                        taxi.pedido_atual = None
                    continue

                elif taxi.estado == "ocupado":
                    taxi.estado = "livre"
                    taxi.objetivo_atual = None
                    if taxi.pedido_atual:
                         taxi.pedido_atual.estado = "concluido"
                    taxi.pedido_atual = None
                    taxi.destino_passageiro = None
                    
                    self.pedidos_completados += 1
                    taxi.viagens_feitas += 1 
                    continue
        
            if taxi.estado in ["livre", "a_abastecer", "a_recolher", "ocupado"]:
                proximo_no = None
                
                if taxi.rota_atual:
                    proximo_no = taxi.rota_atual.pop(0)
                
                elif taxi.estado == "livre":
                    
                    pos_atual = taxi.posicao_atual
                    if len(taxi.historico_movimento) > 0 and taxi.historico_movimento.count(pos_atual) >= 10:
                         proximo_no = random.choice(self.todos_nos)
                         taxi.historico_movimento = []
                    else:
                        try:
                            vizinhos = list(self.G.neighbors(pos_atual))
                            if not vizinhos: vizinhos = list(self.G.predecessors(pos_atual))
                            if vizinhos:
                                opcoes = [v for v in vizinhos if v not in taxi.historico_movimento]
                                proximo_no = random.choice(opcoes) if opcoes else random.choice(vizinhos)
                            else:
                                proximo_no = random.choice(self.todos_nos)
                        except: continue

                if proximo_no:
                    distancia = 0
                    try:
                        distancia = self.G[taxi.posicao_atual][proximo_no][0]['length']
                    except KeyError:
                        try: distancia = self.G[proximo_no][taxi.posicao_atual][0]['length']
                        except: distancia = 0 
                    
                    taxi.mover_para(proximo_no, distancia * self.FATOR_CONSUMO)
        
        self.passo_atual += 1