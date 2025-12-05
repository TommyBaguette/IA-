import os
import time 

def mostrar_menu_principal():
    print("\n" + "="*50)
    print("      TAXI GREEN MATOSINHOS - SISTEMA CENTRAL")
    print("="*50)
    print("--- CONFIGURAÇÃO ---")
    print("1. [SETUP] Criar/Resetar Mapa e Frota")
    print("2. [VER] Visualizar Mapa Estático")
    print("\n--- SIMULAÇÃO E ANÁLISE ---")
    print("3. [VISUAL] Correr Simulação Animada")
    print("4. [BENCHMARK] Comparar Algoritmos (Dijkstra vs A* vs DFS...)")
    print("5. [ANÁLISE] Comparar Frota (Elétrico vs Combustão)")
    print("\n--- SAIR ---")
    print("0. Sair")
    print("="*50)

def obter_escolha():
    return input("\nEscolha uma opção: ").strip()

def pedir_algoritmo():
    print("\n--- ESCOLHA DE ALGORITMO DE NAVEGAÇÃO ---")
    print("1. Dijkstra (Padrão - Melhor caminho real)")
    print("2. A* (A-Star - Heurística otimizada)")
    print("3. Greedy (Sofrego - Muito rápido, caminho não garantido)")
    print("4. BFS (Largura - Ignora distâncias, apenas nº de ruas)")
    print("5. DFS (Profundidade - Caminhos aleatórios/longos)")
    
    escolha = input("\nEscolha o algoritmo (1-5): ").strip()
    mapa = {"1": "dijkstra", "2": "astar", "3": "greedy", "4": "bfs", "5": "dfs"}
    nome = mapa.get(escolha, "dijkstra")
    print(f"-> Algoritmo selecionado: {nome.upper()}")
    return nome

def mostrar_mensagem(msg): print(msg)
def mostrar_erro(erro): print(f"- ERRO: {erro}")
def mostrar_sucesso(sucesso): print(f"\n- SUCESSO: {sucesso}")
def pedir_para_continuar():
    print("\n(A voltar ao menu em 1 segundos...)")
    time.sleep(1) 

def verificar_ficheiros_necessarios(ficheiros):
    for ficheiro, nome_amigavel, solucao in ficheiros:
        if not os.path.exists(ficheiro):
            mostrar_erro(f"Ficheiro '{nome_amigavel}' não encontrado.")
            print(f"  SOLUÇÃO: Executa a {solucao} primeiro.")
            return False
    return True

'''def mostrar_estado_frota(tick, frota_taxis):
    print(f"\n--- TICK {tick} ---")
    for t in frota_taxis:
        km = t.autonomia_atual / 1000.0
        missao = "-> A CARREGAR" if t.estado == "a_abastecer" else ""
        if t.estado == "sem_energia": missao = "!!! MORT !!!"
        print(f"Taxi {t.id} [{t.tipo_motor[0].upper()}]: {km:.2f} km | {t.estado} {missao}") '''

def mostrar_inicio_benchmark(passos, seed):
    print(f"\n=== INICIANDO BENCHMARK DE PERFORMANCE ===")
    print(f"Configuração: {passos} passos | Seed: {seed}")
    print("A carregar dados do mapa...")

def mostrar_progresso_benchmark(alg, tempo, viagens, kms):
    print(f"   >> {alg.upper():<10} | Tempo: {tempo:.2f}s | Viagens: {viagens} | Distância: {kms:.1f} km")

def mostrar_tabela_benchmark(resultados):
    print("\n" + "="*105)
    print(f"{'ALGORITMO':<12} | {'TEMPO(s)':<10} | {'VIAGENS':<8} | {'KMs TOTAIS':<12} | {'CUSTO(€)':<10} | {'PED/KM':<10} | {'€/VIAGEM':<10}")
    print("-" * 105)
    
    for r in resultados:
        print(f"{r['Algoritmo']:<12} | {r['Tempo (s)']:<10} | {r['Viagens']:<8} | "
              f"{r['KMs Totais']:<12} | {r['Custo (€)']:<10} | {r['Pedidos/Km']:<10} | {r['Eficiência (€/V)']:<10}")
    print("="*105)
    

def mostrar_inicio_analise(algoritmo, passos, seed, n_frota):
    print(f"\n=== ANÁLISE: ELÉTRICOS vs COMBUSTÃO ===")
    print(f"Algoritmo: {algoritmo.upper()} | Passos: {passos} | Seed: {seed}")
    print(f"Frota carregada: {n_frota} táxis.")
    print("A processar simulação... (aguarde)")

def mostrar_relatorio_final_frota(stats, tempo):
    e = stats["eletrico"]
    c = stats["combustao"]
    
    e_qtd = e["qtd"] if e["qtd"] > 0 else 1
    c_qtd = c["qtd"] if c["qtd"] > 0 else 1

    e_viagens_media = e["viagens"] / e_qtd
    c_viagens_media = c["viagens"] / c_qtd
    
    e_parado_med = e["parado"] / e_qtd
    c_parado_med = c["parado"] / c_qtd

    print("\n" + "="*80)
    print(f"{'MÉTRICA DE COMPARAÇÃO':<30} | {'ELÉTRICOS':<15} | {'COMBUSTÃO':<15} | {'VENCEDOR':<10}")
    print("-" * 80)
    
    print(f"{'Ticks Parado (Carregar)':<30} | {e_parado_med:<15.1f} | {c_parado_med:<15.1f} | Combustao")
    
    print("-" * 80)

    e_custo_viagem = e["custo"] / e["viagens"] if e["viagens"] > 0 else 0
    c_custo_viagem = c["custo"] / c["viagens"] if c["viagens"] > 0 else 0
    
    venc_prod = "Eletrico" if e_viagens_media > c_viagens_media else "Combustao"
    if abs(e_viagens_media - c_viagens_media) < 0.1: venc_prod = "Empate"
    
    print(f"{'Média Viagens por Táxi':<30} | {e_viagens_media:<15.1f} | {c_viagens_media:<15.1f} | {venc_prod}")
    print(f"{'Total Viagens da Frota':<30} | {e['viagens']:<15} | {c['viagens']:<15} | -")
    print("-" * 80)
    
    print(f"{'Custo Total Operação (€)':<30} | {e['custo']:<15.2f} | {c['custo']:<15.2f} | Eletrico")
    print(f"{'Custo Médio por Viagem (€)':<30} | {e_custo_viagem:<15.2f} | {c_custo_viagem:<15.2f} | Eletrico")
    print("-" * 80)

    venc_amb = "Eletrico" if e['co2'] < c['co2'] else "Combustao"
    print(f"{'Emissões CO2 (kg)':<30} | {e['co2']:<15.2f} | {c['co2']:<15.2f} | {venc_amb}")
    
    print("="*80)
    print(f"Simulação concluída em {tempo:.2f} segundos.")