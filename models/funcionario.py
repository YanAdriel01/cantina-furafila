from models.pessoa import Pessoa
from database.dao.pedido_dao import PedidoDAO
from database.dao.item_dao import ItemDAO
from database.dao.configuracao_dao import ConfiguracaoDAO

class Funcionario(Pessoa):
    """
    Classe Funcionario que herda de Pessoa
    Demonstra HERANÇA
    """
    
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
        """Verifica se a senha está correta"""
        return self.__senha == senha
    
    def alterar_senha(self, nova_senha):
        """Altera a senha do usuário"""
        from database.dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO(self.db_manager)
        if usuario_dao.alterar_senha(self.get_id(), nova_senha):
            self.__senha = nova_senha
            return True
        return False
    
    def aprovar_pedido(self, pedido_id):
        """Aprova um pedido específico"""
        if not self.db_manager:
            return False
        
        return self.pedido_dao.aprovar_pedido(pedido_id)
    
    def abrir_cantina(self):
        """Abre a cantina"""
        if not self.db_manager:
            return False
        
        if not self.config_dao.get_status_cantina():
            self.config_dao.set_status_cantina(True)
            return True
        return False
    
    def fechar_cantina(self):
        """Fecha a cantina"""
        if not self.db_manager:
            return False
        
        if self.config_dao.get_status_cantina():
            self.config_dao.set_status_cantina(False)
            return True
        return False
    
    def atualizar_estoque(self, nome_item, nova_quantidade):
        """Atualiza a quantidade de um item no estoque por nome"""
        if not self.db_manager:
            return False
        
        item = self.item_dao.buscar_por_nome(nome_item)
        if item:
            return self.item_dao.atualizar_quantidade(item['id'], nova_quantidade)
        
        return False
    
    def atualizar_estoque_por_id(self, item_id, nova_quantidade):
        """Atualiza a quantidade de um item no estoque por ID"""
        if not self.db_manager:
            return False
        
        item = self.item_dao.buscar_por_id(item_id)
        if item:
            return self.item_dao.atualizar_quantidade(item_id, nova_quantidade)
        
        return False
    
    def mostrar_informacoes(self):
        """Implementação do método abstrato"""
        return f"👷 Funcionário: {self.get_nome()}, Email: {self.get_email()}"

class Gerente(Funcionario):
    """
    Classe Gerente que herda de Funcionario
    Demonstra HERANÇA - tem todas as funcionalidades do funcionário + administrativas
    """
    
    def __init__(self, user_data=None, nome=None, cpf=None, email=None, senha=None, db_manager=None):
        super().__init__(user_data, nome, cpf, email, senha, db_manager)
    
    def alterar_senha_usuario(self, user_id, nova_senha):
        """Permite ao gerente alterar senha de qualquer usuário"""
        from database.dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO(self.db_manager)
        return usuario_dao.alterar_senha(user_id, nova_senha)
    
    def adicionar_item_estoque(self, nome, preco, quantidade):
        """Adiciona um novo item ao estoque (apenas gerente pode fazer)"""
        if not self.db_manager:
            return False
        
        item_id = self.item_dao.criar_item(nome, preco, quantidade)
        return item_id is not None
    
    def remover_item_estoque(self, nome_item):
        """Remove um item do estoque por nome (apenas gerente pode fazer)"""
        if not self.db_manager:
            return False
        
        item = self.item_dao.buscar_por_nome(nome_item)
        if item:
            return self.item_dao.desativar_item(item['id'])
        
        return False
    
    def remover_item_estoque_por_id(self, item_id):
        """Remove um item do estoque por ID (apenas gerente pode fazer)"""
        if not self.db_manager:
            return False
        
        item = self.item_dao.buscar_por_id(item_id)
        if item:
            return self.item_dao.desativar_item(item_id)
        
        return False
    
    def mostrar_informacoes(self):
        """
        Sobrescreve o método da classe pai
        Demonstra POLIMORFISMO
        """
        return f"👨‍💼 Gerente: {self.get_nome()}, Email: {self.get_email()}"