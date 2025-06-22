import sqlite3
import os
import threading
import time
from contextlib import contextmanager

class DatabaseManager:
    """Gerenciador do banco de dados SQLite com pool de conexões"""
    
    def __init__(self, db_path="cantina.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados criando as tabelas necessárias"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Configurações para melhor performance e evitar locks
            cursor.execute('PRAGMA journal_mode=WAL')
            cursor.execute('PRAGMA synchronous=NORMAL')
            cursor.execute('PRAGMA cache_size=10000')
            cursor.execute('PRAGMA temp_store=MEMORY')
            cursor.execute('PRAGMA busy_timeout=30000')  # 30 segundos de timeout
            
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    senha TEXT NOT NULL,
                    matricula TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de itens do cardápio
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS itens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    preco REAL NOT NULL,
                    quantidade INTEGER NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de pedidos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    total REAL NOT NULL,
                    status TEXT DEFAULT 'pendente',
                    desconto_aplicado REAL DEFAULT 0,
                    metodo_pagamento TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabela de itens do pedido
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pedido_itens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER NOT NULL,
                    item_id INTEGER,
                    item_nome TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                    FOREIGN KEY (item_id) REFERENCES itens (id)
                )
            ''')
            
            # Tabela de configurações da cantina
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT UNIQUE NOT NULL,
                    valor TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco com retry automático"""
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with self._lock:
                    conn = sqlite3.connect(
                        self.db_path, 
                        timeout=30.0,
                        check_same_thread=False
                    )
                    conn.row_factory = sqlite3.Row
                    
                    # Configurações para evitar locks
                    conn.execute('PRAGMA busy_timeout=30000')
                    conn.execute('PRAGMA journal_mode=WAL')
                    
                    try:
                        yield conn
                    finally:
                        conn.close()
                    break
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Backoff exponencial
                    continue
                else:
                    raise
            except Exception:
                raise
    
    def execute_with_retry(self, query, params=None, fetch_one=False, fetch_all=False):
        """Executa query com retry automático em caso de lock"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    if fetch_one:
                        result = cursor.fetchone()
                    elif fetch_all:
                        result = cursor.fetchall()
                    else:
                        result = cursor.rowcount
                    
                    conn.commit()
                    return result
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    raise
    
    def inserir_dados_iniciais(self):
        """Insere dados iniciais no banco de dados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar se já existem dados
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                if cursor.fetchone()[0] > 0:
                    return
                
                # Inserir usuários iniciais
                usuarios_iniciais = [
                    ("Admin", "12345678901", "admin@admin.com", "gerente", "admin123", None),
                    ("Funcionario", "98765432109", "funcionario@funcionario.com", "funcionario", "funcionario123", None),
                    ("Cliente", "11122233344", "cliente@cliente.com", "cliente", "cliente123", None),
                    ("Estudante", "55566677788", "estudante@estudante.com", "estudante", "estudante123", "12345")
                ]
                
                cursor.executemany('''
                    INSERT INTO usuarios (nome, cpf, email, tipo, senha, matricula)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', usuarios_iniciais)
                
                # Inserir itens iniciais
                itens_iniciais = [
                    ("Água Mineral", 2.00, 25),
                    ("Bolo de Chocolate", 6.00, 10),
                    ("Pao de Queijo", 1.65, 30),
                    ("Café", 2.50, 30),
                    ("Coca-Cola", 4.50, 25),
                    ("Sanduíche Natural", 8.50, 20),
                    ("Suco de Laranja", 4.00, 15)
                ]
                
                cursor.executemany('''
                    INSERT INTO itens (nome, preco, quantidade)
                    VALUES (?, ?, ?)
                ''', itens_iniciais)
                
                # Inserir configuração inicial
                cursor.execute('''
                    INSERT INTO configuracoes (chave, valor)
                    VALUES ('cantina_status', 'fechada')
                ''')
                
                conn.commit()
                
        except Exception:
            pass