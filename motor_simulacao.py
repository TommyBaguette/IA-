import random
import networkx as nx
import json
import os

class Taxi:
    def __init__(self, id, no_inicial, tipo_motor, capacidade, autonomia_max):
        self.id = id
        
        # Propriedades Dinâmicas
        self.posicao_atual = no_inicial
        self.autonomia_atual = autonomia_max
        self.estado = "livre" # livre, a_recolher, ocupado, a_reabastecer

        # --- A "MISSÃO" VIVE AQUI ---
        self.objetivo_atual = None # O nó de destino (ex: nó do cliente, nó da bomba)
        self.rota_atual = []       # A lista de nós [A, B, C, ...] para chegar ao objetivo
        # -----------------------------
        
        # Propriedades Estáticas
        self.tipo_motor = tipo_motor
        self.capacidade = capacidade
        self.autonomia_maxima = autonomia_max

    def __repr__(self):
        # Atualizado para mostrar o objetivo
        return (f"Taxi {self.id} ({self.tipo_motor}) | "
                f"Pos: {self.posicao_atual} | "
                f"Estado: {self.estado} | "
                f"Obj: {self.objetivo_atual}")

class MotorSimulacao:
    def __init__(self, G):
        self.G = G
        self.frota_taxis = []
        self.passo_atual = 0

    def criar_frota(self, zonas_recolha, config_file="frota.json"):
        lista_pontos_recolha = []
        for categoria in zonas_recolha.values():
            lista_pontos_recolha.extend(categoria)
        
        if not lista_pontos_recolha:
            return False, "Sem pontos de recolha para posicionar os táxis."

        if not os.path.exists(config_file):
            return False, f"Ficheiro de configuração '{config_file}' não encontrado."
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config_frota = json.load(f)

        for config_taxi in config_frota:
            ponto_inicial = random.choice(lista_pontos_recolha)
            
            novo_taxi = Taxi(
                id=config_taxi["id"],
                no_inicial=ponto_inicial["id_no"],
                tipo_motor=config_taxi["tipo_motor"],
                capacidade=config_taxi["capacidade"],
                autonomia_max=config_taxi["autonomia_max"]
            )
            
            self.frota_taxis.append(novo_taxi)
        
        print(f"Frota de {len(self.frota_taxis)} táxis carregada de '{config_file}'.")
        return True, ""

    def executar_passo(self):
        # Agora, o movimento baseia-se na "missão"
        
        for taxi in self.frota_taxis:
            
            if taxi.estado == "livre":
                
                pos_atual = taxi.posicao_atual
                try:
                    vizinhos = list(self.G.neighbors(pos_atual))
                    if vizinhos:
                        nova_posicao = random.choice(vizinhos)
                        taxi.posicao_atual = nova_posicao
                except nx.NetworkXError:
                    pass
            
            elif taxi.estado == "a_recolher" or taxi.estado == "ocupado":
                # Se tem uma missão...
                if taxi.rota_atual:
                    # ...e a rota não está vazia...
                    
                    # 1. Move o táxi para o próximo nó da rota
                    proximo_no = taxi.rota_atual.pop(0) # Retira o primeiro nó da lista
                    taxi.posicao_atual = proximo_no
                    
                    # 2. (FUTURO) Gastar autonomia
                
                else:
                    if taxi.estado == "a_recolher":
                        print(f"Táxi {taxi.id} chegou à recolha!")
                        # (Aqui mudaria o estado para "ocupado" e receberia a nova rota para o destino)
                        taxi.estado = "livre" # Por agora, fica livre
                    
                    elif taxi.estado == "ocupado":
                        print(f"Táxi {taxi.id} chegou ao destino!")
                        taxi.estado = "livre"
                    
                    taxi.objetivo_atual = None
        
        self.passo_atual += 1