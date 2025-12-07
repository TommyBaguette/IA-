import random
import networkx as nx
import variaveis as var

class GestorTransito:
    def __init__(self, G):
        self.G = G
        for u, v, k, data in self.G.edges(keys=True, data=True):
            data['congestionamento'] = 1.0
            data['tempo_restante_trafego'] = 0
            data['peso_dinamico'] = data['length']

    def atualizar_trafego(self):

        for u, v, k, data in self.G.edges(keys=True, data=True):
            if data['congestionamento'] > 1.0:
                data['tempo_restante_trafego'] -= 1
                
                if data['tempo_restante_trafego'] <= 0:
                    data['congestionamento'] = 1.0
                    data['peso_dinamico'] = data['length'] 

        num_ruas_a_testar = int(self.G.number_of_edges() * 0.1)
        ruas_candidatas = random.sample(list(self.G.edges(keys=True, data=True)), num_ruas_a_testar)

        for u, v, k, data in ruas_candidatas:
            if data['congestionamento'] == 1.0:
                if random.random() < var.PROB_INICIAR_TRANSITO:
                    fator = var.FATOR_TRANSITO_PESADO if random.random() < 0.3 else var.FATOR_TRANSITO_MEDIO
                    
                    data['congestionamento'] = fator
                    data['tempo_restante_trafego'] = var.DURACAO_TRANSITO
                    
                    data['peso_dinamico'] = data['length'] * fator