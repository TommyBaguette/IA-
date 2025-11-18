import gestor_mapa as gm 
import time
import json
import random
import os

def iniciar_simulacao_aleatoria(G):
    """
    Exemplo de uma simulação "Anda Cá".
    Gera 5 pedidos com origem e destino totalmente aleatórios.
    """
    print("\n--- A INICIAR SIMULAÇÃO 'ANDA CÁ' (ALEATÓRIA) ---")
    
    for i in range(5): # Simular 5 pedidos
        print(f"\n[PEDIDO {i+1}/5]")
        
        # 1. Gerar um pedido aleatório de ORIGEM
        pedido_origem = gm.gerar_pedido_local_aleatorio(G)
        print(f"   Origem (Aleatória): Nó {pedido_origem['id_no_origem']}")
        
        # 2. Gerar um pedido aleatório de DESTINO
        pedido_destino = gm.gerar_pedido_local_aleatorio(G)
        print(f"   Destino (Aleatório): Nó {pedido_destino['id_no_origem']}")
        
        # 3. Lógica do teu trabalho (a implementar)
        print("   A calcular rota e táxi mais próximo...")
        # ... (Aqui chamarias a tua função A*, por exemplo)
        
        print("   Pedido atribuído (simulado).")
        time.sleep(1) # Pausa
    
    print("\n--- SIMULAÇÃO TERMINADA ---")

def menu_principal():
    """Menu para escolher entre criar novo ou carregar existente"""
    
    print("\n=== MENU PRINCIPAL - TaxiGreen Matosinhos ===")
    print("--- Setup (Executar 1 vez) ---")
    print("1. [SETUP] Criar mapa base (Estradas + POIs da Frota)")
    print("2. [SETUP] Criar Zonas de Recolha (Hotéis, Hospitais, etc.)")
    print("--- Operações ---")
    print("3. [VER] Carregar e visualizar mapa completo")
    print("4. [RUN] Iniciar simulação de pedidos aleatórios ('Anda Cá')")
    print("5. Sair")
    
    escolha = input("\nEscolha (1-5): ").strip()
    
    if escolha == "1":
        print("A criar mapa base... (pode demorar)")
        gm.criar_mapa_base()
        
    elif escolha == "2":
        print("A criar zonas de recolha... (pode demorar)")
        gm.criar_zonas_recolha() # Chama a nova função

    elif escolha == "3":
        print("A carregar visualização completa...")
        gm.visualizar_mapa_com_pois() # A função atualizada

    elif escolha == "4":
        # Tentar carregar os dados primeiro
        G, pois_frota = gm.carregar_dados() # Carrega o mapa base
        if G:
            iniciar_simulacao_aleatoria(G)
        else:
            print("Mapa não encontrado. Executa a opção 1 primeiro.")

    elif escolha == "5":
        print("Até logo!")
        return False # Sinaliza que deve sair
    
    else:
        print("Escolha inválida")
    
    return True # Sinaliza que deve continuar no menu

if __name__ == "__main__":
    while True: 
        continuar = menu_principal()
        if not continuar:
            break # Sai do loop se o menu_principal retornar False (Opção 5)
            
        input("\n(Premir Enter para voltar ao menu...)")