import json
from Cidade import Cidade
from Carro import Carro
from Graph import Grafo


def carregar_cidades(ficheiro):
    with open(ficheiro, "r", encoding="utf-8") as f:
        dados = json.load(f)
        cidades = []
        for c in dados:
            cidades.append(Cidade(**c))
        return cidades


def carregar_carros(ficheiro):
    with open(ficheiro, "r", encoding="utf-8") as f:
        dados = json.load(f)
        return [Carro(**c) for c in dados]


def construir_grafo(cidades):
    g = Grafo()
    for c in cidades:
        for destino, custo in c.ligacoes:
            g.add_edge(c.getName(), destino, custo)
    return g


def main():
    cidades = carregar_cidades("cidades.json")
    carros = carregar_carros("carros.json")

    grafo = construir_grafo(cidades)

    print("Cidades carregadas:")
    for c in cidades:
        print(" ", c)

    print("Carros carregados:")
    for car in carros:
        print(" ", car)

    print("Arestas do grafo:")
    print(grafo.imprime_aresta())

    # Exemplo: encontrar caminho entre duas cidades
    origem = "Centro"
    destino = "Sul"
    caminho, distancia, tempo = grafo.procura_BFS(origem, destino)
    print(f"\n Caminho {origem} -> {destino}: {caminho} | Distância: {distancia} km | Tempo estimado: {tempo:.2f}h")

if __name__ == "__main__":
    main()
