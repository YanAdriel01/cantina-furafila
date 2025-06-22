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
    
    def atualizar_item(self, item_id, nome=None, preco=None, quantidade=None):
        """Atualiza dados do item"""
        try:
            updates = []
            params = []
            
            if nome:
                updates.append("nome = ?")
                params.append(nome)
            
            if preco is not None:
                updates.append("preco = ?")
                params.append(preco)
            
            if quantidade is not None:
                updates.append("quantidade = ?")
                params.append(quantidade)
            
            if updates:
                params.append(item_id)
                query = f"UPDATE itens SET {', '.join(updates)} WHERE id = ? AND ativo = 1"
                return self.db_manager.execute_with_retry(query, params) > 0
            
            return False
        except Exception:
            return False
    
    def desativar_item(self, item_id):
        """Desativa um item (soft delete)"""
        try:
            return self.db_manager.execute_with_retry(
                'UPDATE itens SET ativo = 0 WHERE id = ?', 
                (item_id,)
            ) > 0
        except Exception:
            return False
    
    def deletar_item_permanente(self, item_id):
        """Deleta um item permanentemente do banco de dados"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar se o item existe em algum pedido
                cursor.execute('''
                    SELECT COUNT(*) as count 
                    FROM pedido_itens 
                    WHERE item_id = ?
                ''', (item_id,))
                
                result = cursor.fetchone()
                if result['count'] > 0:
                    # Se o item está em pedidos, apenas desativar e limpar referência
                    cursor.execute('''
                        UPDATE pedido_itens 
                        SET item_id = NULL 
                        WHERE item_id = ?
                    ''', (item_id,))
                    
                    cursor.execute('UPDATE itens SET ativo = 0 WHERE id = ?', (item_id,))
                else:
                    # Se não está em pedidos, pode deletar permanentemente
                    cursor.execute('DELETE FROM itens WHERE id = ?', (item_id,))
                
                conn.commit()
                return True
                
        except Exception:
            return False
    
    def reativar_item(self, item_id):
        """Reativa um item"""
        try:
            return self.db_manager.execute_with_retry(
                'UPDATE itens SET ativo = 1 WHERE id = ?', 
                (item_id,)
            ) > 0
        except Exception:
            return False