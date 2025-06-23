from models.pessoa import Pessoa
from database.dao.pedido_dao import PedidoDAO
from database.dao.item_dao import ItemDAO
from database.dao.configuracao_dao import ConfiguracaoDAO

class Funcionario(Pessoa):
    """Classe Funcionario que herda de Pessoa"""
    
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
            self.config_dao = ConfiguracaoDAO(db_manager)
    
    def verificar_senha(self, senha):
        return self.__senha == senha
    
    def alterar_senha(self, nova_senha):
        from database.dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO(self.db_manager)
        if usuario_dao.alterar_senha(self.get_id(), nova_senha):
            self.__senha = nova_senha
            return True
        return False
    
    def aprovar_pedido(self, pedido_id):
        if not self.db_manager:
            return False
        return self.pedido_dao.aprovar_pedido(pedido_id)
    
    def mostrar_informacoes(self):
        return f"👷 Funcionário: {self.get_nome()}, Email: {self.get_email()}"

class Gerente(Funcionario):
    """Classe Gerente que herda de Funcionario com funcionalidades administrativas"""
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None, db_manager=None):
        super().__init__(user_data, nome, cpf, email, senha, db_manager)
    
    def adicionar_item_estoque(self, nome, preco, quantidade):
        if not self.db_manager:
            return False
        item_id = self.item_dao.criar_item(nome, preco, quantidade)
        return item_id is not None
    
    def remover_item_estoque_por_id(self, item_id):
        if not self.db_manager:
            return False
        item = self.item_dao.buscar_por_id(item_id)
        if item:
            return self.item_dao.desativar_item(item_id)
        return False
    
    def mostrar_informacoes(self):
        return f"👨‍💼 Gerente: {self.get_nome()}, Email: {self.get_email()}"