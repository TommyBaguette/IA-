# motor_simulacao.py
import random
import json
import os
import networkx as nx
import algoritmos as pf  
from taxi import Taxi
import utils as ut
from alocacao import GestorAlocacao
from gerador_pedidos import GeradorPedidos
import variaveis as var

class MotorSimulacao:
    def __init__(self, G, pois_frota_data, algoritmo="dijkstra"):
        self.G = G
        self.frota_taxis = []
        self.passo_atual = 0
        self.FATOR_CONSUMO = var.FATOR_CONSUMO
        self.pois_frota = pois_frota_data
        self.pedidos_pendentes = []
        self.pedidos_completados = 0
        self.todos_nos = list(self.G.nodes)
        self.algoritmo_escolha = algoritmo
        self.despachante = GestorAlocacao(self.G, self.FATOR_CONSUMO)
        self.gerador = GeradorPedidos(self.G)

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

            novo_taxi.autonomia_atual = novo_taxi.autonomia_maxima 
            self.frota_taxis.append(novo_taxi)
        
        return True, ""

    def encontrar_caminho(self, origem, destino):
        try:
            caminho = pf.calcular_rota(self.algoritmo_escolha, self.G, origem, destino)
            if caminho:
                if self.algoritmo_escolha == "dijkstra":
                    distancia = nx.path_weight(self.G, caminho, weight='length')
                else:
                    distancia = pf.calcular_custo_caminho(self.G, caminho)
                return caminho, distancia
        except: return None, float('inf')
        return None, float('inf')

    def verificar_e_atribuir_abastecimento(self):
        for taxi in self.frota_taxis:
            if taxi.estado != 'livre' or taxi.autonomia_atual <= 0: continue

            threshold = taxi.autonomia_maxima * var.MARGEM_SEGURANCA
            if taxi.autonomia_atual <= threshold:
                
                lista = self.pois_frota.get('carregadores_eletricos', []) if taxi.tipo_motor == 'eletrico' else self.pois_frota.get('bombas_gasolina', [])
                
                dest_id, dist_metros = ut.encontrar_poi_mais_proximo(self.G, taxi.posicao_atual, lista)
                
                if dest_id is None: continue

                custo_real = dist_metros * self.FATOR_CONSUMO
                if (custo_real * 1.10) < taxi.autonomia_atual:
                    caminho, _ = self.encontrar_caminho(taxi.posicao_atual, dest_id)
                    if caminho:
                        if len(caminho) > 0 and caminho[0] == taxi.posicao_atual: caminho.pop(0)
                        taxi.estado = 'a_abastecer' 
                        taxi.objetivo_atual = dest_id
                        taxi.rota_atual = caminho

    def executar_passo(self):
        self.gerador.tentar_gerar(self.passo_atual, self.pedidos_pendentes)
        
        self.despachante.processar_alocacao(self.frota_taxis, self.pedidos_pendentes, self)
        
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
                    rota, _ = self.encontrar_caminho(taxi.posicao_atual, taxi.destino_passageiro)
                    if rota:
                        if len(rota)>0 and rota[0] == taxi.posicao_atual: rota.pop(0)
                        taxi.estado = "ocupado"
                        taxi.rota_atual = rota
                        taxi.objetivo_atual = taxi.destino_passageiro
                    else:
                        taxi.estado = "livre"
                        taxi.pedido_atual = None
                    continue
                elif taxi.estado == "ocupado":
                    taxi.estado = "livre"
                    taxi.objetivo_atual = None
                    if taxi.pedido_atual: taxi.pedido_atual.estado = "concluido"
                    taxi.pedido_atual = None
                    taxi.destino_passageiro = None
                    self.pedidos_completados += 1
                    taxi.viagens_feitas += 1 
                    continue
        
            if taxi.estado in ["livre", "a_abastecer", "a_recolher", "ocupado"]:
                proximo = None
                if taxi.rota_atual: proximo = taxi.rota_atual.pop(0)
                elif taxi.estado == "livre":
                    
                    vizinhos = list(self.G.neighbors(taxi.posicao_atual))
                    if vizinhos: proximo = random.choice(vizinhos)
                
                if proximo:
                    try: dist = self.G[taxi.posicao_atual][proximo][0]['length']
                    except: dist = 0
                    taxi.mover_para(proximo, dist * self.FATOR_CONSUMO)
        
        self.passo_atual += 1