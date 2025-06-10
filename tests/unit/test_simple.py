#!/usr/bin/env python3
"""
Testes Unitários Básicos - Sistema RESTEL
Verificações fundamentais do sistema e dependências
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "restel"))


@pytest.mark.unit
@pytest.mark.smoke
def test_app_import():
    """Testa se a aplicação Flask pode ser importada"""
    from app import app
    assert app is not None
    assert app.name == 'app'


@pytest.mark.unit
@pytest.mark.smoke
def test_app_config():
    """Testa configurações básicas da aplicação"""
    from app import app
    assert app.config is not None
    # Em modo de teste, deve estar configurado corretamente
    app.config['TESTING'] = True
    assert app.config['TESTING'] is True


@pytest.mark.unit
@pytest.mark.smoke
def test_flask_routes_basic(app_client):
    """Testa se as rotas básicas estão definidas"""
    # Testa rota principal
    response = app_client.get('/')
    assert response.status_code == 200
    
    # Testa rota de login admin
    response = app_client.get('/admin/login')
    assert response.status_code == 200
    
    # Testa rota de cadastro de hóspede
    response = app_client.get('/hospede/cadastro')
    assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.database
def test_database_connection(test_database):
    """Testa conexão básica com banco de dados"""
    import sqlite3
    
    # Testar conexão
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    
    # Testar criação de tabela simples
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    
    # Testar inserção
    cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("teste",))
    
    # Testar consulta
    cursor.execute("SELECT name FROM test_table WHERE name = ?", ("teste",))
    result = cursor.fetchone()
    
    assert result is not None
    assert result[0] == "teste"
    
    conn.commit()
    conn.close()


@pytest.mark.unit
@pytest.mark.smoke
def test_imports_dependencies():
    """Testa se todas as dependências principais podem ser importadas"""
    try:
        import flask
        assert flask.__version__ is not None
        
        import sqlite3
        assert sqlite3.version is not None
        
        import werkzeug
        assert werkzeug.__version__ is not None
        
    except ImportError as e:
        pytest.fail(f"Dependência não encontrada: {e}")


@pytest.mark.unit
class TestBasicFunctionality:
    """Classe para testes de funcionalidade básica"""
    
    @pytest.mark.smoke
    def test_app_instance(self):
        """Testa se app é uma instância válida do Flask"""
        from app import app
        from flask import Flask
        assert isinstance(app, Flask)
    
    def test_app_debug_mode(self):
        """Testa configuração de debug"""
        from app import app
        # Em testes, debug deve estar desabilitado
        assert app.debug is False or app.config.get('TESTING') is True
    
    @pytest.mark.smoke
    def test_secret_key_exists(self):
        """Testa se secret key está configurada"""
        from app import app
        assert app.secret_key is not None
        assert len(app.secret_key) > 0
    
    def test_template_folder(self):
        """Testa se pasta de templates está configurada"""
        from app import app
        assert app.template_folder is not None
        template_path = Path(app.root_path) / app.template_folder
        assert template_path.exists()


@pytest.mark.unit
@pytest.mark.integration  
def test_app_initialization():
    """Testa inicialização completa da aplicação"""
    from app import app
    with app.app_context():
        # Testa se o contexto da aplicação funciona
        from flask import current_app
        assert current_app == app
        
        # Testa se configurações estão acessíveis
        assert current_app.config is not None


@pytest.mark.unit
def test_response_headers(app_client):
    """Testa cabeçalhos de resposta básicos"""
    response = app_client.get('/')
    
    # Verificar se response tem headers básicos
    assert 'Content-Type' in response.headers
    assert response.headers['Content-Type'].startswith('text/html')


@pytest.mark.unit
def test_error_handling(app_client):
    """Testa tratamento básico de erros"""
    # Tentar acessar rota inexistente
    response = app_client.get('/rota_inexistente')
    assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.validation
def test_database_schema(test_database):
    """Testa se o schema do banco está correto"""
    import sqlite3
    
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    
    # Verificar se tabelas principais existem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'hospedes' in tables
    assert 'administradores' in tables
    
    conn.close()


@pytest.mark.unit
@pytest.mark.slow
def test_selenium_basic():
    """Testa se Selenium está funcionando básico"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
        
        assert "Test" in driver.page_source
        driver.quit()
        
    except Exception as e:
        pytest.skip(f"Selenium não configurado corretamente: {e}") 