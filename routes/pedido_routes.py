from flask import Blueprint, request, jsonify, session, redirect, url_for, flash, current_app

pedido_bp = Blueprint('pedido', __name__)

@pedido_bp.route('/fazer_pedido', methods=['POST'])
def fazer_pedido():
    """Processar pedido do cliente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não logado'})
    
    if not current_app.cantina.get_status():
        return jsonify({'success': False, 'message': 'Cantina está fechada!'})
    
    try:
        itens_pedido = request.json.get('itens', [])
        metodo_pagamento = request.json.get('metodo_pagamento', 'pix')
        
        if not itens_pedido:
            return jsonify({'success': False, 'message': 'Carrinho vazio!'})
        
        # Validar quantidades
        for item_pedido in itens_pedido:
            if item_pedido['quantidade'] <= 0:
                return jsonify({'success': False, 'message': 'Quantidade deve ser maior que zero!'})
        
        # Buscar dados do usuário
        from database.dao.usuario_dao import UsuarioDAO
        usuario_dao = UsuarioDAO(current_app.db_manager)
        user_data = usuario_dao.buscar_por_id(session['user_id'])
        
        # Criar objeto cliente
        if user_data['tipo'] == 'estudante':
            from models.cliente import ClienteEstudante
            cliente = ClienteEstudante(user_data=user_data, db_manager=current_app.db_manager)
        else:
            from models.cliente import Cliente
            cliente = Cliente(user_data=user_data, db_manager=current_app.db_manager)
        
        # Converter itens para formato esperado
        carrinho = []
        for item_pedido in itens_pedido:
            item = current_app.cantina.buscar_item_por_id(item_pedido['id'])
            if item and item['quantidade'] >= item_pedido['quantidade']:
                carrinho.append((item, item_pedido['quantidade']))
            else:
                return jsonify({'success': False, 'message': f'Estoque insuficiente para {item["nome"] if item else "item"}'})
        
        # Fazer pedido
        if cliente.fazer_pedido(carrinho, metodo_pagamento):
            return jsonify({'success': True, 'message': 'Pedido realizado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao processar pedido'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@pedido_bp.route('/aprovar_pedido/<int:pedido_id>')
def aprovar_pedido(pedido_id):
    """Aprovar pedido (funcionário/gerente)"""
    if 'user_id' not in session or session['user_type'] not in ['funcionario', 'gerente']:
        flash('Acesso negado!', 'error')
        return redirect(url_for('auth.login'))
    
    from database.dao.pedido_dao import PedidoDAO
    pedido_dao = PedidoDAO(current_app.db_manager)
    
    if pedido_dao.aprovar_pedido(pedido_id):
        flash(f'Pedido #{pedido_id} aprovado com sucesso!', 'success')
    else:
        flash('Erro ao aprovar pedido!', 'error')
    
    if session['user_type'] == 'gerente':
        return redirect(url_for('dashboard.gerente'))
    else:
        return redirect(url_for('dashboard.funcionario'))

@pedido_bp.route('/negar_pedido/<int:pedido_id>')
def negar_pedido(pedido_id):
    """Negar pedido e restaurar estoque (funcionário/gerente)"""
    if 'user_id' not in session or session['user_type'] not in ['funcionario', 'gerente']:
        flash('Acesso negado!', 'error')
        return redirect(url_for('auth.login'))
    
    from database.dao.pedido_dao import PedidoDAO
    pedido_dao = PedidoDAO(current_app.db_manager)
    
    if pedido_dao.negar_pedido(pedido_id):
        flash(f'Pedido #{pedido_id} negado e estoque restaurado!', 'success')
    else:
        flash('Erro ao negar pedido!', 'error')
    
    if session['user_type'] == 'gerente':
        return redirect(url_for('dashboard.gerente'))
    else:
        return redirect(url_for('dashboard.funcionario'))