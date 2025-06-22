class Pedido:
    #classe abstrata representando um pedido
    
    _contador_id = 1  # Contador estático para IDs únicos
    
    def __init__(self, cliente, itens):
        #encapsulamento de informações do cliente
        self.__id = Pedido._contador_id
        Pedido._contador_id += 1
        self.__cliente = cliente
        self.__itens = itens
        self.__aprovado = False
    
    #getters para acessar infromações protegidas
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
    
    #setter para settar informações protegidas
    def set_total(self, total):
        self.__total = total
    
    def set_aprovado(self, aprovado):
        self.__aprovado = aprovado
    
    def __str__(self):
        status = "Aprovado" if self.__aprovado else "Pendente"
        return f"Pedido {self.__id} - Cliente: {self.__cliente.get_nome()} - Total: R$ {self.__total:.2f} - Status: {status}"