import os

def mostrar_menu_principal():
    """Imprime o menu principal formatado na consola."""
    print("\n=== MENU PRINCIPAL - TaxiGreen Matosinhos ===")
    print("--- Setup (Executar 1 vez) ---")
    print("1. [SETUP] Criar mapa base (Estradas + POIs da Frota)")
    print("2. [SETUP] Criar Zonas de Recolha (Hotéis, Hospitais, etc.)")
    print("--- Operações ---")
    print("3. [VER] Carregar e visualizar mapa estático")
    print("4. [RUN] Iniciar simulação de pedidos 'Anda Cá' (Texto)")
    print("5. [RUN] Iniciar simulação ANIMADA (Visual)")
    print("6. Sair")

def obter_escolha(num_opcoes=6):
    """Pede ao utilizador uma escolha e retorna-a."""
    return input(f"\nEscolha (1-{num_opcoes}): ").strip()

def pedir_para_continuar():
    """Pede ao utilizador para premir Enter."""
    input("\n(Premir Enter para voltar ao menu...)")

def mostrar_mensagem(mensagem):
    """Imprime uma mensagem standard."""
    print(mensagem)

def mostrar_erro(erro):
    """Imprime uma mensagem de erro formatada."""
    print(f"- ERRO: {erro}")

def mostrar_aviso(aviso):
    """Imprime uma mensagem de aviso formatada."""
    print(f"  - Aviso: {aviso}")

def mostrar_sucesso(sucesso):
    """Imprime uma mensagem de sucesso formatada."""
    print(f"\n- SUCESSO: {sucesso}")

def mostrar_simulacao_texto_resultados(resultados):
    """Imprime os resultados da simulação de texto."""
    print("\n--- A INICIAR SIMULAÇÃO 'ANDA CÁ' (TEXTO) ---")
    for i, (origem, destino) in enumerate(resultados):
        print(f"\n[PEDIDO {i+1}/{len(resultados)}]")
        print(f"   Origem (Aleatória): Nó {origem['id_no_origem']}")
        print(f"   Destino (Aleatório): Nó {destino['id_no_origem']}")
        print("   A calcular rota e táxi mais próximo...")
        print("   Pedido atribuído (simulado).")
    print("\n--- SIMULAÇÃO TERMINADA ---")

def verificar_ficheiros_necessarios(ficheiros):
    """Verifica se uma lista de ficheiros existe e reporta erros."""
    for ficheiro, nome_amigavel, solucao in ficheiros:
        if not os.path.exists(ficheiro):
            mostrar_erro(f"Ficheiro '{nome_amigavel}' não encontrado.")
            mostrar_mensagem(f"  SOLUÇÃO: Executa a {solucao} primeiro.")
            return False
    return True