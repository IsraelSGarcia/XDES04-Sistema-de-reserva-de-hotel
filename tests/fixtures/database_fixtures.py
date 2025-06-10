"""
Fixtures de Banco de Dados - Sistema RESTEL
Fixtures para configuração e manipulação do banco de dados de teste
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_database():
    """Cria banco de dados temporário para toda a sessão de testes"""
    # Criar arquivo temporário
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    # Configurar aplicação com banco de teste
    os.environ['FLASK_TESTING'] = 'True'
    os.environ['TEST_DATABASE'] = temp_db.name
    
    # Importar e configurar app (path já configurado pelo conftest.py raiz)
    from app import app, init_db
    app.config['TESTING'] = True
    app.config['DATABASE'] = temp_db.name
    
    # Inicializar banco
    with app.app_context():
        init_db()
    
    yield temp_db.name
    
    # Cleanup
    os.unlink(temp_db.name)


@pytest.fixture(scope="function")
def clean_database(test_database):
    """Limpa dados do banco entre testes, mantendo estrutura"""
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    
    # Backup do admin padrão
    cursor.execute("SELECT * FROM administradores WHERE email = 'admin@restel.com'")
    admin_backup = cursor.fetchone()
    
    # Limpar dados mas manter estrutura
    cursor.execute("DELETE FROM hospedes")
    cursor.execute("DELETE FROM administradores")
    
    # Restaurar admin padrão se existia
    if admin_backup:
        cursor.execute("""
            INSERT INTO administradores (nome_completo, email, senha, perfil) 
            VALUES (?, ?, ?, ?)
        """, admin_backup[1:])
    
    conn.commit()
    conn.close()
    
    yield test_database


@pytest.fixture(scope="function")
def database_connection(test_database):
    """Fornece conexão direta ao banco de teste"""
    conn = sqlite3.connect(test_database)
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def database_cursor(database_connection):
    """Fornece cursor do banco de teste"""
    cursor = database_connection.cursor()
    yield cursor
    database_connection.commit()


@pytest.fixture(scope="function") 
def empty_database(test_database):
    """Banco completamente vazio para testes específicos"""
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    
    # Limpar todas as tabelas
    cursor.execute("DELETE FROM hospedes")
    cursor.execute("DELETE FROM administradores")
    
    conn.commit()
    conn.close()
    
    yield test_database 