from models.pessoa import Pessoa

class Cliente(Pessoa):
    """
    Classe Cliente que herda de Pessoa
    Demonstra o pilar de HERANÇA
    """
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None):
        super().__init__(user_data, nome, cpf, email)
        if user_data:
            self.__senha = user_data['senha']
        else:
            self.__senha = senha
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return self.__senha == senha
    
    def calcular_total(self, itens_pedido):
        """
        Calcula o total do pedido
        Método que será sobrescrito na classe ClienteEstudante (Polimorfismo)
        """
        total = 0
        for item_data, quantidade in itens_pedido:
            total += item_data['preco'] * quantidade
        return total
    
    def mostrar_informacoes(self):
        """Implementação do método abstrato"""
        return f"Cliente: {self.get_nome()}, Email: {self.get_email()}"

class ClienteEstudante(Cliente):
    """
    Classe ClienteEstudante que herda de Cliente
    Demonstra HERANÇA e POLIMORFISMO (desconto de 10%)
    """
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None, matricula=None):
        super().__init__(user_data, nome, cpf, email, senha)
        if user_data:
            self.__matricula = user_data['matricula']
        else:
            self.__matricula = matricula
        self.__desconto = 0.10  # 10% de desconto
    
    def get_matricula(self):
        return self.__matricula
    
    def calcular_total(self, itens_pedido):
        """
        Sobrescreve o método da classe pai para aplicar desconto
        Demonstra POLIMORFISMO
        """
        total = super().calcular_total(itens_pedido)
        return total  # O desconto será aplicado no método fazer_pedido
    
    def mostrar_informacoes(self):
        """Implementação do método abstrato com informações específicas"""
        return f"🎓 Estudante: {self.get_nome()}, Matrícula: {self.__matricula}, Email: {self.get_email()}"