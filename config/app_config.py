def configure_app(app):
    """Configurações da aplicação Flask"""
    app.secret_key = 'cantina_furafila_secret_key_2024'
    
    # Configurações adicionais podem ser adicionadas aqui
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size