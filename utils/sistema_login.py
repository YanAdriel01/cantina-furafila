from models.funcionario import Gerente, Funcionario
from models.cliente import Cliente, ClienteEstudante
from database.dao.usuario_dao import UsuarioDAO

class SistemaLogin:
    """Sistema de autenticação e gerenciamento de usuários com banco de dados"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.usuario_dao = UsuarioDAO(db_manager)
    
    def login(self, email, senha):
        """Realiza login no sistema"""
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
        
        # Verificar senha
        if not usuario.verificar_senha(senha):
            return None
        
        return usuario
    
    def cadastrar_usuario(self, nome, cpf, email, tipo, senha, matricula=None):
        """Cadastra um novo usuário no sistema"""
        user_id = self.usuario_dao.criar_usuario(nome, cpf, email, tipo, senha, matricula)
        return user_id