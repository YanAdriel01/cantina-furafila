class Pedido:
    """Classe que representa um pedido"""
    
    _contador_id = 1  # Contador estático para IDs únicos
    
    def __init__(self, cliente, itens):
        self.__id = Pedido._contador_id  # Encapsulamento
        Pedido._contador_id += 1
        self.__cliente = cliente  # Encapsulamento
        self.__itens = itens  # Lista de tuplas (item, quantidade)
        self.__total = 0  # Encapsulamento
        self.__aprovado = False  # Encapsulamento
    
    # Getters - Encapsulamento
    def get_id(self):
        return self.__id
    
    def get_cliente(self):
        return self.__cliente
    
    def get_itens(self):
        return self.__itens
    
    def get_total(self):
        return self.__total
    
    def get_aprovado(self):
        return self.__aprovado
    
    # Setters - Encapsulamento
    def set_total(self, total):
        self.__total = total
    
    def set_aprovado(self, aprovado):
        self.__aprovado = aprovado
    
    def __str__(self):
        status = "Aprovado" if self.__aprovado else "Pendente"
        return f"Pedido {self.__id} - Cliente: {self.__cliente.get_nome()} - Total: R$ {self.__total:.2f} - Status: {status}"