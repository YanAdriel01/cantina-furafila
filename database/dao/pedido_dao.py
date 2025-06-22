from database.database_manager import DatabaseManager
import sqlite3

class PedidoDAO:
    """Data Access Object para pedidos"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def criar_pedido(self, cliente_id, total, desconto_aplicado=0, metodo_pagamento="pix"):
        """Cria um novo pedido"""
        try:
            return self.db_manager.execute_with_retry('''
                INSERT INTO pedidos (cliente_id, total, desconto_aplicado, metodo_pagamento, status)
                VALUES (?, ?, ?, ?, 'pendente')
            ''', (cliente_id, total, desconto_aplicado, metodo_pagamento))
        except Exception:
            return None
    
    def adicionar_item_pedido(self, pedido_id, item_id, item_nome, quantidade, preco_unitario):
        """Adiciona um item ao pedido"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO pedido_itens (pedido_id, item_id, item_nome, quantidade, preco_unitario)
                    VALUES (?, ?, ?, ?, ?)
                ''', (pedido_id, item_id, item_nome, quantidade, preco_unitario))
                conn.commit()
                return cursor.lastrowid
        except Exception:
            return None
    
    def buscar_pedidos_cliente(self, cliente_id):
        """Busca todos os pedidos de um cliente com itens"""
        try:
            pedidos_raw = self.db_manager.execute_with_retry('''
                SELECT p.*, u.nome as cliente_nome
                FROM pedidos p
                JOIN usuarios u ON p.cliente_id = u.id
                WHERE p.cliente_id = ?
                ORDER BY p.created_at DESC
            ''', (cliente_id,), fetch_all=True)
            
            pedidos = []
            for pedido_row in pedidos_raw:
                pedido = dict(pedido_row)
                itens = self.buscar_itens_pedido(pedido['id'])
                pedido['itens'] = itens
                pedidos.append(pedido)
            
            return pedidos
        except Exception:
            return []
    
    def buscar_pedidos_pendentes(self):
        """Busca todos os pedidos pendentes"""
        try:
            pedidos_raw = self.db_manager.execute_with_retry('''
                SELECT p.*, u.nome as cliente_nome
                FROM pedidos p
                JOIN usuarios u ON p.cliente_id = u.id
                WHERE p.status = 'pendente'
                ORDER BY p.created_at ASC
            ''', fetch_all=True)
            
            return [dict(row) for row in pedidos_raw]
        except Exception:
            return []
    
    def buscar_itens_pedido(self, pedido_id):
        """Busca os itens de um pedido específico"""
        try:
            itens_raw = self.db_manager.execute_with_retry('''
                SELECT pi.*, 
                       COALESCE(i.nome, pi.item_nome) as item_nome_atual,
                       CASE WHEN i.id IS NULL THEN 1 ELSE 0 END as item_removido
                FROM pedido_itens pi
                LEFT JOIN itens i ON pi.item_id = i.id
                WHERE pi.pedido_id = ?
            ''', (pedido_id,), fetch_all=True)
            
            return [dict(row) for row in itens_raw]
        except Exception:
            return []
    
    def aprovar_pedido(self, pedido_id):
        """Aprova um pedido"""
        try:
            return self.db_manager.execute_with_retry('''
                UPDATE pedidos 
                SET status = 'aprovado', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ? AND status = 'pendente'
            ''', (pedido_id,)) > 0
        except Exception:
            return False
    
    def negar_pedido(self, pedido_id):
        """Nega um pedido e restaura o estoque"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Buscar itens do pedido para restaurar estoque
                cursor.execute('''
                    SELECT item_id, quantidade 
                    FROM pedido_itens 
                    WHERE pedido_id = ? AND item_id IS NOT NULL
                ''', (pedido_id,))
                itens = cursor.fetchall()
                
                # Restaurar estoque de cada item
                for item in itens:
                    cursor.execute('''
                        UPDATE itens 
                        SET quantidade = quantidade + ? 
                        WHERE id = ?
                    ''', (item['quantidade'], item['item_id']))
                
                # Marcar pedido como negado
                cursor.execute('''
                    UPDATE pedidos 
                    SET status = 'negado', updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (pedido_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def buscar_por_id(self, pedido_id):
        """Busca pedido por ID"""
        try:
            pedido_raw = self.db_manager.execute_with_retry('''
                SELECT p.*, u.nome as cliente_nome
                FROM pedidos p
                JOIN usuarios u ON p.cliente_id = u.id
                WHERE p.id = ?
            ''', (pedido_id,), fetch_one=True)
            
            return dict(pedido_raw) if pedido_raw else None
        except Exception:
            return None