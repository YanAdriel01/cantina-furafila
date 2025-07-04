from flask import Blueprint, request, jsonify, session, redirect, url_for, flash, current_app
from utils.validators import validar_cpf, validar_email, validar_matricula

admin_bp = Blueprint('admin', __name__)

def require_admin(user_types):
    """Decorator para verificar permissões administrativas"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session or session['user_type'] not in user_types:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Acesso negado!'})
                flash('Acesso negado!', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@admin_bp.route('/toggle_cantina')
@require_admin(['funcionario', 'gerente'])
def toggle_cantina():
    """Abrir/fechar cantina"""
    status_atual = current_app.cantina.get_status()
    current_app.cantina.set_status(not status_atual)
    
    if status_atual:
        flash('Cantina fechada!', 'info')
    else:
        flash('Cantina aberta!', 'success')
    
    if session['user_type'] == 'gerente':
        return redirect(url_for('dashboard.gerente'))
    else:
        return redirect(url_for('dashboard.funcionario'))

@admin_bp.route('/atualizar_estoque', methods=['POST'])
@require_admin(['funcionario', 'gerente'])
def atualizar_estoque():
    """Atualizar estoque de item"""
    try:
        item_id = int(request.json.get('item_id'))
        nova_quantidade = int(request.json.get('quantidade'))
        
        if nova_quantidade < 0:
            return jsonify({'success': False, 'message': 'Quantidade não pode ser negativa!'})
        
        from database.dao.item_dao import ItemDAO
        item_dao = ItemDAO(current_app.db_manager)
        
        if item_dao.atualizar_quantidade(item_id, nova_quantidade):
            return jsonify({'success': True, 'message': 'Estoque atualizado!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao atualizar estoque!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@admin_bp.route('/adicionar_item', methods=['POST'])
@require_admin(['gerente'])
def adicionar_item():
    """Adicionar novo item (apenas gerente)"""
    try:
        nome = request.json.get('nome', '').strip()
        preco = float(request.json.get('preco'))
        quantidade = int(request.json.get('quantidade'))
        
        if not nome or len(nome) < 2:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 2 caracteres!'})
        
        if preco <= 0:
            return jsonify({'success': False, 'message': 'Preço deve ser maior que zero!'})
        
        if quantidade < 0:
            return jsonify({'success': False, 'message': 'Quantidade não pode ser negativa!'})
        
        from database.dao.item_dao import ItemDAO
        item_dao = ItemDAO(current_app.db_manager)
        
        if item_dao.criar_item(nome, preco, quantidade):
            return jsonify({'success': True, 'message': 'Item adicionado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao adicionar item!'})
            
    except ValueError:
        return jsonify({'success': False, 'message': 'Valores inválidos!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@admin_bp.route('/remover_item/<int:item_id>')
@require_admin(['gerente'])
def remover_item(item_id):
    """Remover item (apenas gerente)"""
    from database.dao.item_dao import ItemDAO
    item_dao = ItemDAO(current_app.db_manager)
    
    if item_dao.deletar_item_permanente(item_id):
        flash('Item removido com sucesso!', 'success')
    else:
        flash('Erro ao remover item!', 'error')
    
    return redirect(url_for('dashboard.gerente'))

@admin_bp.route('/criar_usuario', methods=['POST'])
@require_admin(['gerente'])
def criar_usuario():
    """Criar novo usuário (apenas gerente)"""
    try:
        nome = request.json.get('nome', '').strip()
        cpf = request.json.get('cpf', '').strip()
        email = request.json.get('email', '').strip()
        tipo = request.json.get('tipo', '').strip()
        senha = request.json.get('senha', '').strip()
        matricula = request.json.get('matricula', '').strip() if tipo == 'estudante' else None
        
        if not all([nome, cpf, email, tipo, senha]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios!'})
        
        if len(nome) < 2:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 2 caracteres!'})
        
        if not validar_cpf(cpf):
            return jsonify({'success': False, 'message': 'CPF deve conter apenas 11 números!'})
        
        if not validar_email(email):
            return jsonify({'success': False, 'message': 'Email inválido!'})
        
        if len(senha) < 6:
            return jsonify({'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres!'})
        
        if tipo == 'estudante':
            if not matricula:
                return jsonify({'success': False, 'message': 'Matrícula é obrigatória para estudantes!'})
            if not validar_matricula(matricula):
                return jsonify({'success': False, 'message': 'Matrícula deve conter apenas números!'})
        
        if current_app.sistema_login.cadastrar_usuario(nome, cpf, email, tipo, senha, matricula):
            return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao criar usuário!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@admin_bp.route('/editar_usuario', methods=['POST'])
@require_admin(['gerente'])
def editar_usuario():
    """Editar usuário (apenas gerente)"""
    try:
        user_id = int(request.json.get('id'))
        nome = request.json.get('nome', '').strip()
        email = request.json.get('email', '').strip()
        senha = request.json.get('senha', '').strip()
        tipo = request.json.get('tipo', '').strip()
        matricula = request.json.get('matricula', '').strip()
        
        if nome and len(nome) < 2:
            return jsonify({'success': False, 'message': 'Nome deve ter pelo menos 2 caracteres!'})
        
        if email and not validar_email(email):
            return jsonify({'success': False, 'message': 'Email inválido!'})
        
        if senha and len(senha) < 6:
            return jsonify({'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres!'})
        
        if tipo == 'estudante' and matricula and not validar_matricula(matricula):
            return jsonify({'success': False, 'message': 'Matrícula deve conter apenas números!'})
        
        from database.dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO(current_app.db_manager)
        
        if nome or email:
            if not usuario_dao.atualizar_usuario(user_id, nome, email):
                return jsonify({'success': False, 'message': 'Erro ao atualizar dados básicos!'})
        
        if senha:
            if not usuario_dao.alterar_senha(user_id, senha):
                return jsonify({'success': False, 'message': 'Erro ao alterar senha!'})
        
        if tipo or matricula:
            if not usuario_dao.atualizar_tipo_matricula(user_id, tipo, matricula):
                return jsonify({'success': False, 'message': 'Erro ao atualizar tipo/matrícula!'})
        
        return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@admin_bp.route('/deletar_usuario', methods=['POST'])
@require_admin(['gerente'])
def deletar_usuario():
    """Deletar usuário (apenas gerente)"""
    try:
        user_id = int(request.json.get('user_id'))
        
        if current_app.sistema_login.remover_usuario(user_id):
            return jsonify({'success': True, 'message': 'Usuário deletado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao deletar usuário!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})