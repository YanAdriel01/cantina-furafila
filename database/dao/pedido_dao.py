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
        """Adiciona um item ao pedido com nome do item"""
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
    
    def remover_item_pedido(self, pedido_id, item_id):
        """Remove um item específico do pedido"""
        try:
            return self.db_manager.execute_with_retry('''
                DELETE FROM pedido_itens 
                WHERE pedido_id = ? AND item_id = ?
            ''', (pedido_id, item_id)) > 0
        except Exception:
            return False
    
    def atualizar_quantidade_item_pedido(self, pedido_id, item_id, nova_quantidade):
        """Atualiza a quantidade de um item no pedido"""
        if nova_quantidade <= 0:
            return False
            
        try:
            return self.db_manager.execute_with_retry('''
                UPDATE pedido_itens 
                SET quantidade = ? 
                WHERE pedido_id = ? AND item_id = ?
            ''', (nova_quantidade, pedido_id, item_id)) > 0
        except Exception:
            return False
    
    def atualizar_total_pedido(self, pedido_id):
        """Recalcula e atualiza o total do pedido baseado nos itens"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Calcular novo total
                cursor.execute('''
                    SELECT SUM(quantidade * preco_unitario) as novo_total
                    FROM pedido_itens 
                    WHERE pedido_id = ?
                ''', (pedido_id,))
                
                result = cursor.fetchone()
                novo_total = result['novo_total'] if result['novo_total'] else 0
                
                # Buscar desconto aplicado
                cursor.execute('SELECT desconto_aplicado FROM pedidos WHERE id = ?', (pedido_id,))
                pedido = cursor.fetchone()
                desconto = pedido['desconto_aplicado'] if pedido else 0
                
                # Aplicar desconto se houver
                total_final = novo_total - desconto
                
                # Atualizar total do pedido
                cursor.execute('''
                    UPDATE pedidos 
                    SET total = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (total_final, pedido_id))
                
                conn.commit()
                return total_final
        except Exception:
            return 0
    
    def buscar_pedidos_cliente(self, cliente_id):
        """Busca todos os pedidos de um cliente com itens"""
        try:
            # Buscar pedidos
            pedidos_raw = self.db_manager.execute_with_retry('''
                SELECT p.*, u.nome as cliente_nome
                FROM pedidos p
                JOIN usuarios u ON p.cliente_id = u.id
                WHERE p.cliente_id = ?
                ORDER BY p.created_at DESC
            ''', (cliente_id,), fetch_all=True)
            
            # Converter Row objects para dicionários
            pedidos = []
            for pedido_row in pedidos_raw:
                pedido = dict(pedido_row)
                # Para cada pedido, buscar os itens
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
        """Nega um pedido e restaura o estoque - MANTÉM O PEDIDO NO HISTÓRICO"""
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
                
                # Restaurar estoque de cada item (apenas se o item ainda existir)
                for item in itens:
                    cursor.execute('''
                        UPDATE itens 
                        SET quantidade = quantidade + ? 
                        WHERE id = ?
                    ''', (item['quantidade'], item['item_id']))
                
                # Marcar pedido como negado (NÃO remove do banco)
                cursor.execute('''
                    UPDATE pedidos 
                    SET status = 'negado', updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (pedido_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def salvar_edicao_pedido(self, pedido_id, itens):
        """Salva as edições de um pedido com transação atômica"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Iniciar transação explícita
                    cursor.execute('BEGIN IMMEDIATE')
                    
                    try:
                        # Primeiro, restaurar estoque dos itens atuais
                        cursor.execute('''
                            SELECT pi.item_id, pi.quantidade 
                            FROM pedido_itens pi
                            WHERE pi.pedido_id = ? AND pi.item_id IS NOT NULL
                        ''', (pedido_id,))
                        itens_atuais = cursor.fetchall()
                        
                        for item_atual in itens_atuais:
                            cursor.execute('''
                                UPDATE itens 
                                SET quantidade = quantidade + ? 
                                WHERE id = ?
                            ''', (item_atual['quantidade'], item_atual['item_id']))
                        
                        # Remover todos os itens atuais do pedido
                        cursor.execute('DELETE FROM pedido_itens WHERE pedido_id = ?', (pedido_id,))
                        
                        # Adicionar os novos itens e atualizar estoque
                        for item in itens:
                            if item['quantidade'] <= 0:
                                continue
                            
                            # Buscar informações do item
                            cursor.execute('SELECT nome, quantidade FROM itens WHERE id = ?', (item['item_id'],))
                            item_info = cursor.fetchone()
                            
                            if item_info and item_info['quantidade'] < item['quantidade']:
                                raise Exception(f"Estoque insuficiente para o item ID {item['item_id']}")
                            
                            # Adicionar item ao pedido
                            cursor.execute('''
                                INSERT INTO pedido_itens (pedido_id, item_id, item_nome, quantidade, preco_unitario)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (pedido_id, item['item_id'], item_info['nome'] if item_info else 'Item Removido', 
                                  item['quantidade'], item['preco_unitario']))
                            
                            # Atualizar estoque (apenas se o item ainda existir)
                            if item_info:
                                cursor.execute('''
                                    UPDATE itens 
                                    SET quantidade = quantidade - ? 
                                    WHERE id = ?
                                ''', (item['quantidade'], item['item_id']))
                        
                        # Recalcular total do pedido
                        cursor.execute('''
                            SELECT SUM(quantidade * preco_unitario) as novo_total
                            FROM pedido_itens 
                            WHERE pedido_id = ?
                        ''', (pedido_id,))
                        
                        result = cursor.fetchone()
                        novo_total = result['novo_total'] if result['novo_total'] else 0
                        
                        # Buscar desconto aplicado
                        cursor.execute('SELECT desconto_aplicado FROM pedidos WHERE id = ?', (pedido_id,))
                        pedido = cursor.fetchone()
                        desconto = pedido['desconto_aplicado'] if pedido else 0
                        
                        # Aplicar desconto se houver
                        total_final = novo_total - desconto
                        
                        # Atualizar total do pedido
                        cursor.execute('''
                            UPDATE pedidos 
                            SET total = ?, updated_at = CURRENT_TIMESTAMP 
                            WHERE id = ?
                        ''', (total_final, pedido_id))
                        
                        # Confirmar transação
                        cursor.execute('COMMIT')
                        return True
                        
                    except Exception as e:
                        cursor.execute('ROLLBACK')
                        raise e
                        
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    import time
                    time.sleep(0.2 * (attempt + 1))
                    continue
                else:
                    return False
            except Exception:
                return False
        
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