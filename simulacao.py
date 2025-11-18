import gestor_mapa as gm
import motor_simulacao as ms
import visualizador as vis
import view_consola as vc
import time
import json
import os

class Controlador:
    def __init__(self):
        # O controlador conhece os seus modelos e vistas
        self.gestor_mapa = gm
        self.motor_simulacao = ms.MotorSimulacao
        self.view_consola = vc
        self.view_grafica = vis
        self.a_correr = True

    def run(self):
        """Loop principal da aplicação."""
        while self.a_correr:
            self.view_consola.mostrar_menu_principal()
            escolha = self.view_consola.obter_escolha(6)
            
            if escolha == '1':
                self.acao_criar_mapa_base()
            elif escolha == '2':
                self.acao_criar_zonas_recolha()
            elif escolha == '3':
                self.acao_visualizar_mapa_estatico()
            elif escolha == '4':
                self.acao_simulacao_texto()
            elif escolha == '5':
                self.acao_simulacao_animada()
            elif escolha == '6':
                self.acao_sair()
            else:
                self.view_consola.mostrar_erro("Escolha inválida")
            
            if self.a_correr:
                self.view_consola.pedir_para_continuar()

    def acao_criar_mapa_base(self):
        self.view_consola.mostrar_mensagem("A criar mapa base... (pode demorar)")
        self.gestor_mapa.criar_mapa_base()
        self.view_consola.mostrar_sucesso("Mapa base criado.")

    def acao_criar_zonas_recolha(self):
        self.view_consola.mostrar_mensagem("A criar zonas de recolha... (pode demorar)")
        # Verificar se o mapa base existe primeiro
        if not self.view_consola.verificar_ficheiros_necessarios([
            ("matosinhos_5km.graphml", "Grafo de estradas", "opção 1")
        ]):
            return

        if self.gestor_mapa.criar_zonas_recolha():
            self.view_consola.mostrar_sucesso("Zonas de recolha criadas.")
        else:
            self.view_consola.mostrar_erro("Não foi possível criar zonas de recolha.")

    def acao_visualizar_mapa_estatico(self):
        self.view_consola.mostrar_mensagem("A carregar visualização completa...")
        self.gestor_mapa.visualizar_mapa_com_pois()

    def acao_simulacao_texto(self):
        G, _ = self.gestor_mapa.carregar_dados()
        if not G:
            self.view_consola.mostrar_erro("Dados do mapa não carregados. Executa a opção 1.")
            return

        resultados = []
        for _ in range(5):
            origem = self.gestor_mapa.gerar_pedido_local_aleatorio(G)
            destino = self.gestor_mapa.gerar_pedido_local_aleatorio(G)
            resultados.append((origem, destino))
            time.sleep(0.5) # Simular o tempo de processamento
        
        self.view_consola.mostrar_simulacao_texto_resultados(resultados)

    def acao_simulacao_animada(self, num_taxis=15, passos_simulacao=100):
        self.view_consola.mostrar_mensagem("A preparar simulação animada...")

        # 1. Verificar e carregar dados do Modelo
        if not self.view_consola.verificar_ficheiros_necessarios([
            ("matosinhos_5km.graphml", "Grafo de estradas", "opção 1"),
            ("pontos_interesse_matoshinhos.json", "POIs da Frota", "opção 1"),
            ("zonas_recolha_matosinhos.json", "Zonas de Recolha", "opção 2")
        ]):
            return
            
        G, pois_frota = self.gestor_mapa.carregar_dados()
        zonas_recolha = {}
        try:
            with open("zonas_recolha_matosinhos.json", "r", encoding="utf-8") as f:
                zonas_recolha = json.load(f)
        except Exception as e:
            self.view_consola.mostrar_erro(f"Não foi possível ler as zonas de recolha: {e}")
            return

        # 2. Preparar o Modelo (Motor)
        sim = self.motor_simulacao(G)
        if not sim.criar_frota(num_taxis, zonas_recolha):
            self.view_consola.mostrar_erro("Não foi possível criar a frota. Sem pontos de recolha.")
            return

        # 3. Preparar a Vista Gráfica
        fig, ax = self.view_grafica.preparar_janela()
        self.view_consola.mostrar_mensagem("A iniciar simulação... (Fecha a janela do mapa para parar)")

        # 4. Loop do Controlador
        for _ in range(passos_simulacao):
            # 4.1. Atualizar o Modelo
            sim.executar_passo()
            
            # 4.2. Atualizar a Vista Gráfica
            continuar = self.view_grafica.desenhar_frame(
                ax=ax,
                G=G,
                pois_frota=pois_frota,
                frota_taxis=sim.frota_taxis,
                passo_atual=sim.passo_atual,
                passos_totais=passos_simulacao
            )
            
            if not continuar:
                self.view_consola.mostrar_mensagem("Janela fechada. Simulação terminada.")
                break
        
        self.view_grafica.fechar_janela()
        self.view_consola.mostrar_sucesso("Simulação animada terminada.")

    def acao_sair(self):
        self.view_consola.mostrar_mensagem("Até logo!")
        self.a_correr = False

if __name__ == "__main__":
    controlador = Controlador()
    controlador.run()