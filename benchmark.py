import time
import csv
import gestor_mapa as gm
import motor_simulacao as ms
import view as vc 
import variaveis as var
import random

# Configurações do Benchmark
PASSOS = var.PASSOS_SIMULACAO 
SEED = var.SEED_PADRAO
ALGORITMOS_A_TESTAR = ["dijkstra", "astar", "greedy", "bfs", "dfs"]

def correr_benchmark():

    G, pois_frota = gm.carregar_dados()
    
    if not G:
        vc.mostrar_erro("Mapa não encontrado.")
        return

    resultados = []

    vc.mostrar_inicio_benchmark(PASSOS, SEED)

    for algo in ALGORITMOS_A_TESTAR:
       
        random.seed(SEED)
        
        sim = ms.MotorSimulacao(G, pois_frota, algoritmo=algo)
        sim.criar_frota() 
        
        acumulador_ocupacao = 0 
        
        start_time = time.time()
        
        for _ in range(PASSOS):
            sim.executar_passo()
            
            taxis_ocupados_agora = sum(1 for t in sim.frota_taxis if t.estado == "ocupado")
            acumulador_ocupacao += taxis_ocupados_agora

        tempo_execucao = time.time() - start_time

        # --- CÁLCULO DAS MÉTRICAS DO ENUNCIADO ---
        
        total_viagens = sim.pedidos_completados
        total_km = sum(t.custo_total / t.custo_por_km for t in sim.frota_taxis if t.custo_por_km > 0)
        custo_total = sum(t.custo_total for t in sim.frota_taxis)
        
        custo_por_viagem = (custo_total / total_viagens) if total_viagens > 0 else 0.0
        
        lista_esperas = getattr(sim, 'tempos_espera_totais', [])
        tempo_medio_espera = sum(lista_esperas) / len(lista_esperas) if lista_esperas else 0.0
        
        total_ticks_possiveis = len(sim.frota_taxis) * PASSOS
        taxa_ocupacao = (acumulador_ocupacao / total_ticks_possiveis) * 100 if total_ticks_possiveis > 0 else 0.0
        
        pedidos_falhados = len(sim.pedidos_pendentes)

        resultados.append({
            "Algoritmo": algo.upper(),
            "Tempo(s)": round(tempo_execucao, 4),
            "Viagens": total_viagens,
            "KMs Totais": round(total_km, 1),
            "Custo Total": round(custo_total, 2),
            "Custo/Viagem": round(custo_por_viagem, 2),
            "Espera Media": round(tempo_medio_espera, 1),
            "Ocupacao (%)": round(taxa_ocupacao, 1),
            "Falhados": pedidos_falhados
        })

    vc.mostrar_tabela_benchmark(resultados)

    nome_csv = "resultados_benchmark_final.csv"
    try:
        keys = resultados[0].keys()
        with open(nome_csv, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(resultados)
        vc.mostrar_sucesso(f"Relatório completo guardado em '{nome_csv}'")
    except Exception as e:
        vc.mostrar_erro(f"Ao guardar CSV: {e}")

if __name__ == "__main__":
    correr_benchmark()