import gestor_mapa as gm
import motor_simulacao as ms
import visualizador as vis
import view as vc
import time
import json
import os

class Controlador:
    def __init__(self):
        self.gestor_mapa = gm
        self.motor_simulacao = ms.MotorSimulacao
        self.view_consola = vc
        self.view_grafica = vis
        self.a_correr = True

    def run(self):
        while self.a_correr:
            self.view_consola.mostrar_menu_principal()
            escolha = self.view_consola.obter_escolha(5)
            
            if escolha == '1':
                self.acao_criar_mapa_base()
            elif escolha == '2':
                self.acao_criar_zonas_recolha()
            elif escolha == '3':
                self.acao_visualizar_mapa_estatico()
            elif escolha == '4':
                self.acao_simulacao_animada()
            elif escolha == '5':
                self.acao_sair()
            else:
                self.view_consola.mostrar_erro("Escolha invalida")
            
            if self.a_correr:
                self.view_consola.pedir_para_continuar()

    def acao_criar_mapa_base(self):
        self.view_consola.mostrar_mensagem("A criar mapa base...")
        self.gestor_mapa.criar_mapa_base()
        self.view_consola.mostrar_sucesso("Mapa base criado.")

    def acao_criar_zonas_recolha(self):
        self.view_consola.mostrar_mensagem("A criar zonas de recolha...")
        if not self.view_consola.verificar_ficheiros_necessarios([
            ("matosinhos_5km.graphml", "Grafo de estradas", "opcao 1")
        ]):
            return

        if self.gestor_mapa.criar_zonas_recolha():
            self.view_consola.mostrar_sucesso("Zonas de recolha criadas.")
        else:
            self.view_consola.mostrar_erro("Nao foi possivel criar zonas de recolha.")

    def acao_visualizar_mapa_estatico(self):
        self.view_consola.mostrar_mensagem("A carregar visualizacao completa...")
        self.gestor_mapa.visualizar_mapa_com_pois()

    def acao_simulacao_animada(self, passos_simulacao=1000):
        self.view_consola.mostrar_mensagem("A preparar simulacao animada...")

        if not self.view_consola.verificar_ficheiros_necessarios([
            ("matosinhos_5km.graphml", "Grafo de estradas", "opcao 1"),
            ("pontos_interesse_matoshinhos.json", "POIs da Frota", "opcao 1"),
            ("zonas_recolha_matosinhos.json", "Zonas de Recolha", "opcao 2"),
            ("frota.json", "Configuracao da Frota", "criar o ficheiro")
        ]):
            return
            
        G, pois_frota = self.gestor_mapa.carregar_dados()
        zonas_recolha = {}
        try:
            with open("zonas_recolha_matosinhos.json", "r", encoding="utf-8") as f:
                zonas_recolha = json.load(f)
        except Exception as e:
            self.view_consola.mostrar_erro(f"Nao foi possivel ler as zonas de recolha: {e}")
            return
        
        plotar_bombas, plotar_carregadores, plotar_recolha = self.gestor_mapa.filtrar_pontos_com_hierarquia(
            pois_frota, zonas_recolha, 250
        )

        sim = self.motor_simulacao(G, pois_frota)
        
        zonas_filtradas_dict = {"recolha": plotar_recolha}
        sucesso, mensagem_erro = sim.criar_frota(zonas_filtradas_dict, "frota.json")
        if not sucesso:
            self.view_consola.mostrar_erro(f"Nao foi possivel criar a frota: {mensagem_erro}")
            return

        fig, ax = self.view_grafica.preparar_janela()
        self.view_consola.mostrar_mensagem("A iniciar simulacao...")

        self.view_grafica.desenhar_fundo_mapa(ax, G, 
                                              plotar_bombas, 
                                              plotar_carregadores, 
                                              plotar_recolha)
        
        artists_frame_anterior = []

        for i in range(passos_simulacao):
            sim.executar_passo()
            
            self.view_consola.mostrar_estado_frota(i + 1, sim.frota_taxis)
            
            artists_frame_anterior, continuar = self.view_grafica.desenhar_frame_animado(
                ax=ax,
                G=G,
                frota_taxis=sim.frota_taxis,
                artists_anteriores=artists_frame_anterior
            )
            
            if not continuar:
                self.view_consola.mostrar_mensagem("Janela fechada. Simulacao terminada.")
                break
        
        self.view_grafica.fechar_janela()
        self.view_consola.mostrar_sucesso("Simulacao animada terminada.")

    def acao_sair(self):
        self.view_consola.mostrar_mensagem("Ate logo!")
        self.a_correr = False

if __name__ == "__main__":
    controlador = Controlador()
    controlador.run()