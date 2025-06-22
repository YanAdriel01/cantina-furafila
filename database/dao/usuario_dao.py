from database.database_manager import DatabaseManager
import sqlite3

class UsuarioDAO:
    """Data Access Object para usuários"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def criar_usuario(self, nome, cpf, email, tipo, senha, matricula=None):
        """Cria um novo usuário no banco"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO usuarios (nome, cpf, email, tipo, senha, matricula)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (nome, cpf, email, tipo, senha, matricula))
                    conn.commit()
                    return cursor.lastrowid
                    
            except sqlite3.IntegrityError:
                return None
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    import time
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    return None
            except Exception:
                return None
        
        return None
    
    def buscar_por_email(self, email):
        """Busca usuário por email"""
        try:
            user_raw = self.db_manager.execute_with_retry(
                'SELECT * FROM usuarios WHERE email = ?', 
                (email,), 
                fetch_one=True
            )
            return dict(user_raw) if user_raw else None
        except Exception:
            return None
    
    def buscar_por_id(self, user_id):
        """Busca usuário por ID"""
        try:
            user_raw = self.db_manager.execute_with_retry(
                'SELECT * FROM usuarios WHERE id = ?', 
                (user_id,), 
                fetch_one=True
            )
            return dict(user_raw) if user_raw else None
        except Exception:
            return None
    
    def listar_todos(self):
        """Lista todos os usuários ordenados por ID"""
        try:
            users_raw = self.db_manager.execute_with_retry(
                'SELECT * FROM usuarios ORDER BY id', 
                fetch_all=True
            )
            return [dict(row) for row in users_raw]
        except Exception:
            return []
    
    def atualizar_usuario(self, user_id, nome=None, email=None):
        """Atualiza dados básicos do usuário"""
        try:
            updates = []
            params = []
            
            if nome:
                updates.append("nome = ?")
                params.append(nome)
            
            if email:
                updates.append("email = ?")
                params.append(email)
            
            if updates:
                params.append(user_id)
                query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
                return self.db_manager.execute_with_retry(query, params) > 0
            
            return False
        except Exception:
            return False
    
    def atualizar_tipo_matricula(self, user_id, tipo=None, matricula=None):
        """Atualiza tipo e matrícula do usuário"""
        try:
            updates = []
            params = []
            
            if tipo:
                updates.append("tipo = ?")
                params.append(tipo)
            
            if matricula is not None:  # Permite string vazia para remover matrícula
                updates.append("matricula = ?")
                params.append(matricula if matricula else None)
            
            if updates:
                params.append(user_id)
                query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
                return self.db_manager.execute_with_retry(query, params) > 0
            
            return False
        except Exception:
            return False
    
    def alterar_senha(self, user_id, nova_senha):
        """Altera a senha de um usuário"""
        try:
            return self.db_manager.execute_with_retry(
                'UPDATE usuarios SET senha = ? WHERE id = ?', 
                (nova_senha, user_id)
            ) > 0
        except Exception:
            return False
    
    def deletar_usuario(self, user_id):
        """Deleta um usuário"""
        try:
            return self.db_manager.execute_with_retry(
                'DELETE FROM usuarios WHERE id = ?', 
                (user_id,)
            ) > 0
        except Exception:
            return False