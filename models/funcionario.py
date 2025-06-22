from models.pessoa import Pessoa

class Funcionario(Pessoa):
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None):
        super().__init__(user_data, nome, cpf, email)
        if user_data:
            self.__senha = user_data['senha']
        else:
            self.__senha = senha
    
    def verificar_senha(self, senha):
        return self.__senha == senha
    
    def mostrar_informacoes(self):
        return f"👷 Funcionário: {self.get_nome()}, Email: {self.get_email()}"

class Gerente(Funcionario):
   
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None):
        super().__init__(user_data, nome, cpf, email, senha)
    
    def mostrar_informacoes(self):

        return f"👨‍💼 Gerente: {self.get_nome()}, Email: {self.get_email()}"