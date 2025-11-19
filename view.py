import os
import time 

def mostrar_menu_principal():
    print("\n=== MENU PRINCIPAL - TaxiGreen Matosinhos ===")
    print("--- Setup (Executar 1 vez) ---")
    print("1. [SETUP] Criar mapa base (Estradas + POIs da Frota)")
    print("2. [SETUP] Criar Zonas de Recolha (Hotéis, Hospitais, etc.)")
    print("--- Operações ---")
    print("3. [VER] Carregar e visualizar mapa estático")
    print("4. [RUN] Iniciar simulação ANIMADA (Visual)")
    print("5. Sair")

def obter_escolha(num_opcoes=5):
    return input(f"\nEscolha (1-{num_opcoes}): ").strip()

def pedir_para_continuar():
    print("\n(A voltar ao menu em 2 segundos...)")
    time.sleep(2) 

def mostrar_mensagem(mensagem):
    print(mensagem)

def mostrar_erro(erro):
    print(f"- ERRO: {erro}")

def mostrar_aviso(aviso):
    print(f"  - Aviso: {aviso}")

def mostrar_sucesso(sucesso):
    print(f"\n- SUCESSO: {sucesso}")

def mostrar_estado_frota(tick, frota_taxis):
    """Imprime o estado da frota e a missão de abastecimento a cada passo."""
    print(f"\n--- TICK {tick} ---")
    for t in frota_taxis:
        km_restantes = t.autonomia_atual / 1000.0
        
        status_missao = ""
        if t.estado == "a_abastecer":
            status_missao = "-> DESTINO: ABASTECIMENTO!"
        elif t.estado == "sem_energia":
            status_missao = "!!! PARADO: SEM ENERGIA !!!"

        print(f"Taxi {t.id} [{t.tipo_motor.upper()}]: {km_restantes:.2f} km | Est: {t.estado} {status_missao}")

def verificar_ficheiros_necessarios(ficheiros):
    for ficheiro, nome_amigavel, solucao in ficheiros:
        if not os.path.exists(ficheiro):
            mostrar_erro(f"Ficheiro '{nome_amigavel}' não encontrado.")
            mostrar_mensagem(f"  SOLUÇÃO: Executa a {solucao} primeiro.")
            return False
    return True