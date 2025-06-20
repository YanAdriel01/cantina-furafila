from flask import Flask
from config.app_config import configure_app
from routes.auth_routes import auth_bp
from database.database_manager import DatabaseManager
from utils.sistema_login import SistemaLogin

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurar aplicação
    configure_app(app)
    
    # Inicializar sistema
    db_manager = DatabaseManager()
    db_manager.inserir_dados_iniciais()
    sistema_login = SistemaLogin(db_manager)
    
    # Disponibilizar instâncias globalmente
    app.db_manager = db_manager
    app.sistema_login = sistema_login
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)