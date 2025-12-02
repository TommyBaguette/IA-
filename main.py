import sys
import view as vc
import simulacao
import benchmark
import taxicompare
import gestor_mapa

def main():
    ctrl_visual = simulacao.Controlador()

    while True:

        vc.mostrar_menu_principal()
        opcao = vc.obter_escolha()

        if opcao == '1':
            vc.mostrar_mensagem("A criar mapa...")
            gestor_mapa.criar_mapa_base()
            vc.mostrar_sucesso("Mapa criado.")
            
        elif opcao == '2':
            gestor_mapa.visualizar_mapa_com_pois()
            
        elif opcao == '3':
            ctrl_visual.acao_simulacao_animada()
            
        elif opcao == '4':
            benchmark.correr_benchmark()
            
        elif opcao == '5':
            taxicompare.analisar_frota()
            
        elif opcao == '0':
            vc.mostrar_mensagem("A sair...")
            sys.exit()
            
        else:
            vc.mostrar_erro("Opção inválida!")
    
        vc.pedir_para_continuar()

if __name__ == "__main__":
    main()