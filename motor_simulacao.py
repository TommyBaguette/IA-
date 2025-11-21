import random
import networkx as nx
import json
import os
import math

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def heuristica(G, node_a, node_b):
    lat1 = G.nodes[node_a]['y']
    lon1 = G.nodes[node_a]['x']
    lat2 = G.nodes[node_b]['y']
    lon2 = G.nodes[node_b]['x']
    return calcular_distancia_haversine(lat1, lon1, lat2, lon2)

class Taxi:
    def __init__(self, id, no_inicial, tipo_motor, capacidade, autonomia_max):
        self.id = id
        self.posicao_atual = no_inicial
        
        self.historico_movimento = [] #utilizado para debug
        
        self.objetivo_atual = None 
        self.rota_atual = []       
        
        self.autonomia_maxima = autonomia_max * 1000
        self.autonomia_atual = self.autonomia_maxima
        self.custo_total = 0.0
        self.emissoes_CO2 = 0.0
        self.estado = "livre" 
        
        self.tipo_motor = tipo_motor
        self.capacidade = capacidade
        
        if self.tipo_motor == "eletrico":
            self.velocidade_carregamento = 500
            self.custo_por_km = 0.06
            self.emissao_por_km = 0.0
        else:
            self.velocidade_carregamento = self.autonomia_maxima
            self.custo_por_km = 0.30
            self.emissao_por_km = 0.11

    def mover_para(self, novo_no, distancia_metros):
        self.historico_movimento.append(self.posicao_atual)
        if len(self.historico_movimento) > 20:
            self.historico_movimento.pop(0)
            
        self.posicao_atual = novo_no
        self.autonomia_atual -= distancia_metros
        
        custo_viagem = (distancia_metros / 1000.0) * self.custo_por_km
        emissoes_viagem = (distancia_metros / 1000.0) * self.emissao_por_km
        self.custo_total += custo_viagem
        self.emissoes_CO2 += emissoes_viagem

        if self.autonomia_atual <= 0:
            self.autonomia_atual = 0
            self.estado = "sem_energia"

    def carregar(self):
        if self.autonomia_atual < self.autonomia_maxima:
            self.autonomia_atual += self.velocidade_carregamento
            if self.autonomia_atual > self.autonomia_maxima:
                self.autonomia_atual = self.autonomia_maxima
            return False
        else:
            self.historico_movimento = []
            return True 

    def __repr__(self):
        km_restantes = self.autonomia_atual / 1000
        return (f"Taxi {self.id} ({self.tipo_motor}) | Aut: {km_restantes:.1f}km | Est: {self.estado}")

class MotorSimulacao:
    def __init__(self, G, pois_frota_data):
        self.G = G
        self.frota_taxis = []
        self.passo_atual = 0
        self.FATOR_CONSUMO = 1.0
        self.pois_frota = pois_frota_data

    def criar_frota(self, zonas_recolha, config_file="frota.json"):
        lista_pontos_recolha = []
        for categoria in zonas_recolha.values():
            lista_pontos_recolha.extend(categoria)
        
        if not lista_pontos_recolha: return False, "Sem pontos de recolha."

        if not os.path.exists(config_file): return False, f"Ficheiro '{config_file}' não encontrado."
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config_frota = json.load(f)

        for i, config_taxi in enumerate(config_frota):
            ponto_inicial = random.choice(lista_pontos_recolha)
            novo_taxi = Taxi(
                id=config_taxi["id"],
                no_inicial=ponto_inicial["id_no"],
                tipo_motor=config_taxi["tipo_motor"],
                capacidade=config_taxi["capacidade"],
                autonomia_max=config_taxi["autonomia_max"]
            )
        

            self.frota_taxis.append(novo_taxi)
        
        return True, ""

    def encontrar_caminho(self, origem, destino):
        try:
            caminho = nx.dijkstra_path(self.G, origem, destino, weight='length')
            distancia = nx.path_weight(self.G, caminho, weight='length')
            return caminho, distancia
        except nx.NetworkXNoPath:
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

    def verificar_e_atribuir_abastecimento(self):
        for taxi in self.frota_taxis:
            if taxi.estado != 'livre' or taxi.autonomia_atual <= 0:
                continue

            threshold = taxi.autonomia_maxima * 0.20 
            
            if taxi.autonomia_atual <= threshold:
                destino_abastecimento, dist_metros = self.encontrar_poi_mais_proximo(taxi)
                
                if destino_abastecimento is None:
                    continue

                custo_real_viagem = dist_metros * self.FATOR_CONSUMO
                margem_seguranca = custo_real_viagem * 1.10

                if margem_seguranca < taxi.autonomia_atual:
                    caminho, _ = self.encontrar_caminho(taxi.posicao_atual, destino_abastecimento)
                    if caminho:
                        taxi.estado = 'a_abastecer' 
                        taxi.objetivo_atual = destino_abastecimento
                        taxi.rota_atual = caminho

    def executar_passo(self):
        self.verificar_e_atribuir_abastecimento()

        for taxi in self.frota_taxis:
            
            if taxi.estado == "sem_energia":
                continue

            if taxi.estado == "a_abastecer" and taxi.posicao_atual == taxi.objetivo_atual:
                esta_cheio = taxi.carregar()
                if esta_cheio:
                    taxi.estado = "livre"
                    taxi.objetivo_atual = None
                continue 
            
            if taxi.estado == "livre" or taxi.estado == "a_abastecer":
                
                proximo_no = None
                
                if taxi.rota_atual:
                    proximo_no = taxi.rota_atual.pop(0)
                
                elif taxi.estado == "livre":
                    pos_atual = taxi.posicao_atual
                    
                    if taxi.historico_movimento.count(pos_atual) >= 10:
                        todos_nos = list(self.G.nodes)
                        proximo_no = random.choice(todos_nos)
                        taxi.historico_movimento = [] 
                    else:
                        try:
                            vizinhos = list(self.G.neighbors(pos_atual))
                            if not vizinhos: 
                                vizinhos = list(self.G.predecessors(pos_atual))
                            
                            if vizinhos:
                                proximo_no = random.choice(vizinhos)
                            else:
                                todos_nos = list(self.G.nodes)
                                proximo_no = random.choice(todos_nos)
                                taxi.historico_movimento = []

                        except (nx.NetworkXError, KeyError, IndexError):
                            continue

                if proximo_no:
                    distancia = 0
                    try:
                        distancia = self.G[taxi.posicao_atual][proximo_no][0]['length']
                    except KeyError:
                        try:
                            distancia = self.G[proximo_no][taxi.posicao_atual][0]['length']
                        except KeyError:
                            distancia = 0 
                    
                    distancia_consumida = distancia * self.FATOR_CONSUMO
                    taxi.mover_para(proximo_no, distancia_consumida)
        
        self.passo_atual += 1