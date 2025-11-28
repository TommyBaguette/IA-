class Taxi:
    def __init__(self, id, no_inicial, tipo_motor, capacidade, autonomia_max):
        self.id = id
        self.posicao_atual = no_inicial
        
        self.historico_movimento = []
        
        self.objetivo_atual = None 
        self.rota_atual = []
        self.destino_passageiro = None 
        
        self.autonomia_maxima = autonomia_max * 1000
        self.autonomia_atual = self.autonomia_maxima
        self.custo_total = 0.0
        self.emissoes_CO2 = 0.0
        self.viagens_feitas = 0
        self.ticks_a_carregar = 0
        self.estado = "livre" 
        
        self.tipo_motor = tipo_motor
        self.capacidade = capacidade
        
        if self.tipo_motor == "eletrico":
            self.velocidade_carregamento = 10
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