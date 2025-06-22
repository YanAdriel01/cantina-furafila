from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from utils.validators import validar_cpf, validar_email, validar_matricula

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Página inicial"""
    cardapio = current_app.cantina.get_cardapio()
    status_cantina = current_app.cantina.get_status()
    return render_template('index.html', cardapio=cardapio, status_cantina=status_cantina)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form['email'].strip()
        senha = request.form['senha']
        
        # Validações básicas
        if not email or not senha:
            flash('Email e senha são obrigatórios!', 'error')
            return render_template('login.html')
        
        if not validar_email(email):
            flash('Email inválido!', 'error')
            return render_template('login.html')
        
        usuario = current_app.sistema_login.login(email, senha)
        if usuario:
            session['user_id'] = usuario.get_id()
            session['user_name'] = usuario.get_nome()
            session['user_type'] = usuario.__class__.__name__.lower()
            flash(f'Bem-vindo, {usuario.get_nome()}!', 'success')
            
            # Redirecionar baseado no tipo de usuário
            if session['user_type'] == 'gerente':
                return redirect(url_for('dashboard.gerente'))
            elif session['user_type'] == 'funcionario':
                return redirect(url_for('dashboard.funcionario'))
            else:
                return redirect(url_for('dashboard.cliente'))
        else:
            flash('Email ou senha incorretos!', 'error')
    
    return render_template('login.html')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Página de cadastro com validações"""
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
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template('cadastro.html')
        
        if not validar_cpf(cpf):
            flash('CPF deve conter apenas 11 números!', 'error')
            return render_template('cadastro.html')
        
        if not validar_email(email):
            flash('Email inválido!', 'error')
            return render_template('cadastro.html')
        
        if len(senha) < 6:
            flash('Senha deve ter pelo menos 6 caracteres!', 'error')
            return render_template('cadastro.html')
        
        if eh_estudante and not validar_matricula(matricula):
            flash('Matrícula deve conter apenas números!', 'error')
            return render_template('cadastro.html')
        
        if current_app.sistema_login.cadastrar_usuario(nome, cpf, email, tipo, senha, matricula):
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Erro no cadastro. Verifique se o email ou CPF já não estão em uso.', 'error')
    
    return render_template('cadastro.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.index'))