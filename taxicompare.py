import time
import random
import gestor_mapa as gm
import motor_simulacao as ms
import view as vc 

PASSOS = 1000
SEED = 42
ALGORITMO = "dijkstra"

def analisar_frota():
    G, pois_frota = gm.carregar_dados()
    if not G:
        vc.mostrar_erro("Mapa não encontrado.")
        return

    random.seed(SEED)
    sim = ms.MotorSimulacao(G, pois_frota, algoritmo=ALGORITMO)
    sucesso, msg = sim.criar_frota()
    
    if not sucesso:
        vc.mostrar_erro(f"Erro ao criar frota: {msg}")
        return
    
    vc.mostrar_inicio_analise(ALGORITMO, PASSOS, SEED, len(sim.frota_taxis))

    start = time.time()
    for _ in range(PASSOS):
        sim.executar_passo()
    tempo_total = time.time() - start

    stats = {
        "eletrico":   {"qtd": 0, "km": 0.0, "custo": 0.0, "co2": 0.0, "viagens": 0},
        "combustao":  {"qtd": 0, "km": 0.0, "custo": 0.0, "co2": 0.0, "viagens": 0}
    }

    for taxi in sim.frota_taxis:
        tipo = "eletrico" if taxi.tipo_motor == "eletrico" else "combustao"
        
        km_percorridos = 0
        if taxi.custo_por_km > 0:
            km_percorridos = taxi.custo_total / taxi.custo_por_km
        
        stats[tipo]["qtd"] += 1
        stats[tipo]["km"] += km_percorridos
        stats[tipo]["custo"] += taxi.custo_total
        stats[tipo]["co2"] += taxi.emissoes_CO2
        stats[tipo]["viagens"] += taxi.viagens_feitas
        if "parado" not in stats[tipo]: stats[tipo]["parado"] = 0
        stats[tipo]["parado"] += taxi.ticks_a_carregar

    vc.mostrar_relatorio_final_frota(stats, tempo_total)

if __name__ == "__main__":
    analisar_frota()