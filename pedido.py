class Pedido:
    def __init__(self, id_pedido, origem, destino, origem_coords):
        self.id = id_pedido
        self.origem = origem
        self.destino = destino
        self.origem_coords = origem_coords 
        
        self.estado = "pendente" 
        self.tempo_espera = 0 

    def __repr__(self):
        return f"Pedido {self.id} ({self.origem} -> {self.destino})"