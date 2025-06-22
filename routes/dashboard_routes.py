from flask import Blueprint, render_template, session, redirect, url_for, current_app

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def require_login(user_types=None):
    """Decorator para verificar login"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            if user_types and session.get('user_type') not in user_types:
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@dashboard_bp.route('/cliente')
@require_login(['cliente', 'clienteestudante'])
def cliente():
    """Dashboard do cliente"""
    from database.dao.usuario_dao import UsuarioDAO
    from database.dao.pedido_dao import PedidoDAO
    
    usuario_dao = UsuarioDAO(current_app.db_manager)
    pedido_dao = PedidoDAO(current_app.db_manager)
    
    user_data = usuario_dao.buscar_por_id(session['user_id'])
    pedidos = pedido_dao.buscar_pedidos_cliente(session['user_id'])
    cardapio = current_app.cantina.get_cardapio()
    status_cantina = current_app.cantina.get_status()
    
    return render_template('dashboard_cliente.html', 
                         user_data=user_data, 
                         pedidos=pedidos, 
                         cardapio=cardapio,
                         status_cantina=status_cantina)

@dashboard_bp.route('/funcionario')
@require_login(['funcionario'])
def funcionario():
    """Dashboard do funcionário"""
    pedidos_pendentes = current_app.cantina.get_pedidos_pendentes()
    cardapio = current_app.cantina.get_cardapio()
    status_cantina = current_app.cantina.get_status()
    
    return render_template('dashboard_funcionario.html', 
                         pedidos_pendentes=pedidos_pendentes,
                         cardapio=cardapio,
                         status_cantina=status_cantina)

@dashboard_bp.route('/gerente')
@require_login(['gerente'])
def gerente():
    """Dashboard do gerente"""
    from database.dao.usuario_dao import UsuarioDAO
    usuario_dao = UsuarioDAO(current_app.db_manager)
    
    pedidos_pendentes = current_app.cantina.get_pedidos_pendentes()
    cardapio = current_app.cantina.get_cardapio()
    usuarios = usuario_dao.listar_todos()
    status_cantina = current_app.cantina.get_status()
    
    return render_template('dashboard_gerente.html', 
                         pedidos_pendentes=pedidos_pendentes,
                         cardapio=cardapio,
                         usuarios=usuarios,
                         status_cantina=status_cantina)