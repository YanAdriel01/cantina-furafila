from models.pessoa import Pessoa

class Funcionario(Pessoa):
    #Classe abstrata representando um funcionário no sistema, é subclasse de Pessoa
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None):
        super().__init__(user_data, nome, cpf, email)
        if user_data:
            self.__senha = user_data['senha']
        else:
            self.__senha = senha
    
    def verificar_senha(self, senha):
        #método usado para verificar a senha
        return self.__senha == senha
    
    def mostrar_informacoes(self):
        #método para mostrar informações usando getters
        return f" Funcionário: {self.get_nome()}, Email: {self.get_email()}"

class Gerente(Funcionario):
    #Essa classe abstrata representa um gerente que possui outras permissões, subclasse de Funcionario
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None):
        super().__init__(user_data, nome, cpf, email, senha)
    
    def mostrar_informacoes(self):
        #usando o mesmo método de Funcionario para mostrar informações protegidas
        return f"Gerente: {self.get_nome()}, Email: {self.get_email()}"