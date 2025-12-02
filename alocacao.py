# Ficheiro: alocacao.py
import networkx as nx
import utils as ut

class GestorAlocacao:
    def __init__(self, G, fator_consumo):
        self.G = G
        self.FATOR_CONSUMO = fator_consumo

    def processar_alocacao(self, frota_taxis, pedidos_pendentes, motor_ref):
        """
        Recebe a frota e os pedidos, e decide quem vai buscar quem.
        """
        for pedido in pedidos_pendentes:
            if pedido.estado != "pendente": continue

            candidatos = []
            
            # Estimativa para o destino
            dist_viagem_estimada = ut.heuristica(self.G, pedido.origem, pedido.destino)

            for taxi in frota_taxis:
                if taxi.estado == "livre":
                    # Regra de Segurança da Bateria
                    margem_reserva_taxi = taxi.autonomia_maxima * 0.25
                    if taxi.autonomia_atual < margem_reserva_taxi:
                        continue 

                    # Heurística até ao cliente
                    dist_h = ut.heuristica(self.G, taxi.posicao_atual, pedido.origem)
                    candidatos.append((dist_h, taxi))

            if not candidatos: continue

            # Escolher TOP 3
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
                # Pede ao motor para calcular o caminho final (usando o algoritmo escolhido lá)
                caminho, _ = motor_ref.encontrar_caminho(melhor_taxi.posicao_atual, pedido.origem)
                
                if caminho:
                    if len(caminho) > 0 and caminho[0] == melhor_taxi.posicao_atual:
                        caminho.pop(0)
                        
                    melhor_taxi.estado = "a_recolher"
                    melhor_taxi.rota_atual = caminho
                    melhor_taxi.objetivo_atual = pedido.origem
                    melhor_taxi.destino_passageiro = pedido.destino
                    melhor_taxi.pedido_atual = pedido 
                    pedido.estado = "atribuido"