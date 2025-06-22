from flask import Flask
from config.app_config import configure_app
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.pedido_routes import pedido_bp
from database.database_manager import DatabaseManager
from models.cantina import Cantina
from utils.sistema_login import SistemaLogin

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurar aplicação
    configure_app(app)
    
    # Inicializar sistema
    db_manager = DatabaseManager()
    db_manager.inserir_dados_iniciais()
    cantina = Cantina(db_manager)
    sistema_login = SistemaLogin(db_manager)
    
    # Abrir cantina inicialmente
    cantina.set_status(True)
    
    # Disponibilizar instâncias globalmente
    app.db_manager = db_manager
    app.cantina = cantina
    app.sistema_login = sistema_login
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pedido_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)