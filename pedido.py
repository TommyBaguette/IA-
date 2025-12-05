class Pedido:
    def __init__(self, id_pedido, origem, destino, origem_coords, premium=False, eco=False):
        self.id = id_pedido
        self.origem = origem
        self.destino = destino
        self.origem_coords = origem_coords
        self.estado = "pendente"
        self.premium = premium
        self.eco_friendly = eco

    def __repr__(self):
        p_str = "[PREMIUM]" if self.premium else ""
        e_str = "[ECO]" if self.eco_friendly else ""
        return f"Pedido {self.id} {p_str}{e_str}"