from models.pessoa import Pessoa

class Funcionario(Pessoa):
    """
    Classe Funcionario que herda de Pessoa
    Demonstra HERANÇA
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
    
    def mostrar_informacoes(self):
        """Implementação do método abstrato"""
        return f"👷 Funcionário: {self.get_nome()}, Email: {self.get_email()}"

class Gerente(Funcionario):
    """
    Classe Gerente que herda de Funcionario
    Demonstra HERANÇA - tem todas as funcionalidades do funcionário + administrativas
    """
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None):
        super().__init__(user_data, nome, cpf, email, senha)
    
    def mostrar_informacoes(self):
        """
        Sobrescreve o método da classe pai
        Demonstra POLIMORFISMO
        """
        return f"👨‍💼 Gerente: {self.get_nome()}, Email: {self.get_email()}"