from models.funcionario import Gerente, Funcionario
from models.cliente import Cliente, ClienteEstudante
from database.dao.usuario_dao import UsuarioDAO

class SistemaLogin:
    """Sistema de autenticação e gerenciamento de usuários com banco de dados"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.usuario_dao = UsuarioDAO(db_manager)
    
    def login(self, email, senha):
        """
        Realiza login no sistema
        Agora TODOS os usuários precisam de senha
        """
        user_data = self.usuario_dao.buscar_por_email(email)
        
        if not user_data:
            return None
        
        # Criar objeto baseado no tipo de usuário
        if user_data['tipo'] == 'gerente':
            usuario = Gerente(user_data=user_data, db_manager=self.db_manager)
        elif user_data['tipo'] == 'funcionario':
            usuario = Funcionario(user_data=user_data, db_manager=self.db_manager)
        elif user_data['tipo'] == 'estudante':
            usuario = ClienteEstudante(user_data=user_data, db_manager=self.db_manager)
        else:  # cliente
            usuario = Cliente(user_data=user_data, db_manager=self.db_manager)
        
        # Verificar senha para todos os tipos de usuário
        if not usuario.verificar_senha(senha):
            return None
        
        return usuario
    
    def cadastrar_usuario(self, nome, cpf, email, tipo, senha, matricula=None):
        """Cadastra um novo usuário no sistema"""
        user_id = self.usuario_dao.criar_usuario(nome, cpf, email, tipo, senha, matricula)
        return user_id
    
    def editar_usuario(self, user_id, novo_nome=None, novo_email=None):
        """Edita informações de um usuário (apenas gerentes podem fazer)"""
        return self.usuario_dao.atualizar_usuario(user_id, novo_nome, novo_email)
    
    def remover_usuario(self, user_id):
        """Remove um usuário do sistema (apenas gerentes podem fazer)"""
        return self.usuario_dao.deletar_usuario(user_id)
    
    def buscar_usuario_por_id(self, user_id):
        """Busca usuário por ID"""
        return self.usuario_dao.buscar_por_id(user_id)