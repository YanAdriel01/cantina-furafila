from database.database_manager import DatabaseManager

class ConfiguracaoDAO:
    """Data Access Object para configurações do sistema"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_configuracao(self, chave):
        """Busca uma configuração por chave"""
        try:
            result = self.db_manager.execute_with_retry(
                'SELECT valor FROM configuracoes WHERE chave = ?', 
                (chave,), 
                fetch_one=True
            )
            return result['valor'] if result else None
        except Exception:
            return None
    
    def set_configuracao(self, chave, valor):
        """Define uma configuração"""
        try:
            self.db_manager.execute_with_retry('''
                INSERT OR REPLACE INTO configuracoes (chave, valor, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (chave, valor))
            return True
        except Exception:
            return False
    
    def get_status_cantina(self):
        """Retorna o status da cantina"""
        try:
            status = self.get_configuracao('cantina_status')
            return status == 'aberta'
        except Exception:
            return False
    
    def set_status_cantina(self, aberta):
        """Define o status da cantina"""
        try:
            status = 'aberta' if aberta else 'fechada'
            return self.set_configuracao('cantina_status', status)
        except Exception:
            return False