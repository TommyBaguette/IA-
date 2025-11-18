import random
import networkx as nx

class Taxi:
    def __init__(self, id, no_inicial):
        self.id = id
        self.posicao_atual = no_inicial
        # Futuramente:
        # self.autonomia = 100 
        # self.tipo_motor = "eletrico"
        # self.estado = "livre" # ou "a_recolher", "ocupado"

class MotorSimulacao:
    def __init__(self, G):
        self.G = G
        self.frota_taxis = []
        self.passo_atual = 0

    def criar_frota(self, num_taxis, zonas_recolha):
        lista_pontos_recolha = []
        for categoria in zonas_recolha.values():
            lista_pontos_recolha.extend(categoria)
        
        if not lista_pontos_recolha:
            # Não imprimimos, retornamos falha
            return False

        for i in range(num_taxis):
            ponto_inicial = random.choice(lista_pontos_recolha)
            novo_taxi = Taxi(id=i, no_inicial=ponto_inicial["id_no"])
            self.frota_taxis.append(novo_taxi)
        
        return True

    def executar_passo(self):
        # Lógica de movimento (atualmente aleatória)
        for taxi in self.frota_taxis:
            # No futuro: verificar se o taxi tem um objetivo (cliente, etc.)
            # Se não tiver, move-se aleatoriamente
            
            pos_atual = taxi.posicao_atual
            try:
                vizinhos = list(self.G.neighbors(pos_atual))
                if vizinhos:
                    nova_posicao = random.choice(vizinhos)
                    taxi.posicao_atual = nova_posicao
            except nx.NetworkXError:
                pass 
        
        self.passo_atual += 1