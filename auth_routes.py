from flask import Blueprint, request, redirect, url_for, session, flash, current_app
from utils.validators import validar_cpf, validar_email, validar_matricula

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Página inicial"""
    return "<h1>Cantina FuraFila</h1><p><a href='/login'>Fazer Login</a></p>"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email'].strip()
        senha = request.form['senha']
        
        # Validações básicas
        if not email or not senha:
            return "Email e senha são obrigatórios!"
        
        if not validar_email(email):
            return "Email inválido!"
        
        usuario = current_app.sistema_login.login(email, senha)
        if usuario:
            session['user_id'] = usuario.get_id()
            session['user_name'] = usuario.get_nome()
            session['user_type'] = usuario.__class__.__name__.lower()
            
            return f"Login realizado com sucesso! Bem-vindo, {usuario.get_nome()}!"
        else:
            return "Email ou senha incorretos!"
    
    return '''
    <form method="POST">
        <h2>Login</h2>
        <p>Email: <input type="email" name="email" required></p>
        <p>Senha: <input type="password" name="senha" required></p>
        <p><input type="submit" value="Entrar"></p>
    </form>
    <p><a href="/cadastro">Cadastrar-se</a></p>
    '''

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Página de cadastro"""
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        cpf = request.form['cpf'].strip()
        email = request.form['email'].strip()
        senha = request.form['senha'].strip()
        eh_estudante = 'eh_estudante' in request.form
        matricula = request.form.get('matricula', '').strip() if eh_estudante else None
        tipo = 'estudante' if eh_estudante else 'cliente'
        
        # Validações
        if not nome or not cpf or not email or not senha:
            return "Todos os campos são obrigatórios!"
        
        if not validar_cpf(cpf):
            return "CPF deve conter apenas 11 números!"
        
        if not validar_email(email):
            return "Email inválido!"
        
        if len(senha) < 6:
            return "Senha deve ter pelo menos 6 caracteres!"
        
        if eh_estudante and not validar_matricula(matricula):
            return "Matrícula deve conter apenas números!"
        
        if current_app.sistema_login.cadastrar_usuario(nome, cpf, email, tipo, senha, matricula):
            return "Cadastro realizado com sucesso! <a href='/login'>Fazer login</a>"
        else:
            return "Erro no cadastro. Verifique se o email ou CPF já não estão em uso."
    
    return '''
    <form method="POST">
        <h2>Cadastro</h2>
        <p>Nome: <input type="text" name="nome" required></p>
        <p>CPF: <input type="text" name="cpf" maxlength="11" required></p>
        <p>Email: <input type="email" name="email" required></p>
        <p>Senha: <input type="password" name="senha" required></p>
        <p><input type="checkbox" name="eh_estudante"> Sou estudante (10% desconto)</p>
        <p>Matrícula (se estudante): <input type="text" name="matricula"></p>
        <p><input type="submit" value="Cadastrar"></p>
    </form>
    <p><a href="/login">Já tem conta? Fazer login</a></p>
    '''

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    return "Logout realizado com sucesso! <a href='/'>Voltar ao início</a>"