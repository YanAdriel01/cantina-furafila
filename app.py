from flask import Flask
from config.app_config import configure_app
from database.database_manager import DatabaseManager

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurar aplicação
    configure_app(app)
    
    # Inicializar sistema
    db_manager = DatabaseManager()
    db_manager.inserir_dados_iniciais()
    
    # Disponibilizar instâncias globalmente
    app.db_manager = db_manager
    
    @app.route('/')
    def index():
        return "<h1>Cantina FuraFila - Sistema com Banco de Dados</h1><p>Banco SQLite configurado com sucesso!</p>"
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)