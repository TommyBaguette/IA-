import time
import random
import csv
import gestor_mapa as gm
import motor_simulacao as ms
import view as vc  # Importar a View

# --- CONFIGURAÇÕES ---
PASSOS_SIMULACAO = 500
SEED_FIXA = 42
ALGORITMOS_A_TESTAR = ["dijkstra", "astar", "greedy", "bfs", "dfs"]

def correr_benchmark():
    vc.mostrar_inicio_benchmark(PASSOS_SIMULACAO, SEED_FIXA)
    
    G, pois_frota = gm.carregar_dados()
    if G is None:
        vc.mostrar_erro("Mapa não encontrado. Executa o setup primeiro.")
        return

    resultados = []

    for alg in ALGORITMOS_A_TESTAR:
        random.seed(SEED_FIXA)
        
        sim = ms.MotorSimulacao(G, pois_frota, algoritmo=alg)
        sucesso, msg = sim.criar_frota(config_file="frota.json")
        
        if not sucesso:
            vc.mostrar_erro(f"Erro frota: {msg}")
            continue

        start_time = time.time()
        for _ in range(PASSOS_SIMULACAO):
            sim.executar_passo()
        tempo_execucao = time.time() - start_time
        
        total_custo = sum(t.custo_total for t in sim.frota_taxis)
        taxis_mortos = sum(1 for t in sim.frota_taxis if t.estado == "sem_energia")
        viagens = sim.pedidos_completados
        eficiencia = round(total_custo / viagens, 2) if viagens > 0 else 0.0

        vc.mostrar_progresso_benchmark(alg, tempo_execucao, viagens, total_custo)

        dados = {
            "Algoritmo": alg.upper(),
            "Tempo (s)": round(tempo_execucao, 4),
            "Viagens": viagens,
            "Custo (€)": round(total_custo, 2),
            "Mortos": taxis_mortos,
            "Eficiência (€/V)": eficiencia
        }
        resultados.append(dados)

    vc.mostrar_tabela_benchmark(resultados)
    guardar_csv(resultados)

def guardar_csv(resultados):
    if not resultados: return
    filename = "resultados_benchmark.csv"
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(resultados)
        vc.mostrar_sucesso(f"CSV guardado em '{filename}'")
    except Exception as e:
        vc.mostrar_erro(f"Falha ao guardar CSV: {e}")

if __name__ == "__main__":
    correr_benchmark()