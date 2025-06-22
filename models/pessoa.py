from abc import ABC, abstractmethod

class Pessoa(ABC):
    """Classe abstrata que representa uma pessoa no sistema"""
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None):
        if user_data:
            self._id = user_data['id']
            self.__nome = user_data['nome']
            self.__cpf = user_data['cpf']
            self.__email = user_data['email']
        else:
            self._id = None
            self.__nome = nome
            self.__cpf = cpf
            self.__email = email
    
    def get_id(self):
        return self._id
    
    def get_nome(self):
        return self.__nome
    
    def get_cpf(self):
        return self.__cpf
    
    def get_email(self):
        return self.__email
    
    def set_nome(self, nome):
        self.__nome = nome
    
    def set_email(self, email):
        self.__email = email
    
    @abstractmethod
    def mostrar_informacoes(self):
        """Método abstrato que deve ser implementado pelas classes filhas"""
        pass