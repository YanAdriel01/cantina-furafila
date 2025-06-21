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