from models.pessoa import Pessoa
from database.dao.pedido_dao import PedidoDAO
from database.dao.item_dao import ItemDAO

class Cliente(Pessoa):
    """Classe Cliente que herda de Pessoa"""
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None, db_manager=None):
        super().__init__(user_data, nome, cpf, email)
        if user_data:
            self.__senha = user_data['senha']
        else:
            self.__senha = senha
        self.db_manager = db_manager
        if db_manager:
            self.pedido_dao = PedidoDAO(db_manager)
            self.item_dao = ItemDAO(db_manager)
    
    def verificar_senha(self, senha):
        return self.__senha == senha
    
    def alterar_senha(self, nova_senha):
        from database.dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO(self.db_manager)
        if usuario_dao.alterar_senha(self.get_id(), nova_senha):
            self.__senha = nova_senha
            return True
        return False
    
    def fazer_pedido(self, itens_pedido, metodo_pagamento):
        """Cria um novo pedido no banco de dados"""
        if not self.db_manager:
            return False
        
        total = self.calcular_total(itens_pedido)
        desconto = 0
        
        if isinstance(self, ClienteEstudante):
            desconto = total * 0.10
            total = total - desconto
        
        pedido_id = self.pedido_dao.criar_pedido(self.get_id(), total, desconto, metodo_pagamento)
        
        if pedido_id:
            for item_data, quantidade in itens_pedido:
                self.pedido_dao.adicionar_item_pedido(
                    pedido_id, item_data['id'], item_data['nome'], quantidade, item_data['preco']
                )
                nova_quantidade = item_data['quantidade'] - quantidade
                self.item_dao.atualizar_quantidade(item_data['id'], nova_quantidade)
            return True
        return False
    
    def calcular_total(self, itens_pedido):
        total = 0
        for item_data, quantidade in itens_pedido:
            total += item_data['preco'] * quantidade
        return total
    
    def mostrar_informacoes(self):
        return f"Cliente: {self.get_nome()}, Email: {self.get_email()}"

class ClienteEstudante(Cliente):
    """Classe ClienteEstudante que herda de Cliente com desconto de 10%"""
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None, matricula=None, db_manager=None):
        super().__init__(user_data, nome, cpf, email, senha, db_manager)
        if user_data:
            self.__matricula = user_data['matricula']
        else:
            self.__matricula = matricula
    
    def get_matricula(self):
        return self.__matricula
    
    def mostrar_informacoes(self):
        return f"🎓 Estudante: {self.get_nome()}, Matrícula: {self.__matricula}, Email: {self.get_email()}"