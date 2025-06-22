from database.database_manager import DatabaseManager

class ItemDAO:
    """Data Access Object para itens do cardápio"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def criar_item(self, nome, preco, quantidade):
        """Cria um novo item no cardápio"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO itens (nome, preco, quantidade)
                    VALUES (?, ?, ?)
                ''', (nome, preco, quantidade))
                conn.commit()
                return cursor.lastrowid
        except Exception:
            return None
    
    def buscar_por_nome(self, nome):
        """Busca item por nome"""
        try:
            item_raw = self.db_manager.execute_with_retry(
                'SELECT * FROM itens WHERE nome = ? AND ativo = 1', 
                (nome,), 
                fetch_one=True
            )
            return dict(item_raw) if item_raw else None
        except Exception:
            return None
    
    def buscar_por_id(self, item_id):
        """Busca item por ID"""
        try:
            item_raw = self.db_manager.execute_with_retry(
                'SELECT * FROM itens WHERE id = ? AND ativo = 1', 
                (item_id,), 
                fetch_one=True
            )
            return dict(item_raw) if item_raw else None
        except Exception:
            return None
    
    def listar_ativos(self):
        """Lista todos os itens ativos ordenados por ID"""
        try:
            itens_raw = self.db_manager.execute_with_retry(
                'SELECT * FROM itens WHERE ativo = 1 ORDER BY id', 
                fetch_all=True
            )
            return [dict(row) for row in itens_raw]
        except Exception:
            return []
    
    def atualizar_quantidade(self, item_id, nova_quantidade):
        """Atualiza quantidade do item"""
        try:
            return self.db_manager.execute_with_retry('''
                UPDATE itens SET quantidade = ? WHERE id = ? AND ativo = 1
            ''', (nova_quantidade, item_id)) > 0
        except Exception:
            return False