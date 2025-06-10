"""
Configuração Principal de Testes - Sistema RESTEL
Configurações centralizadas, fixtures e utilitários compartilhados
"""

import pytest
import sqlite3
import tempfile
import shutil
import os
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from unittest.mock import patch
import time
import threading
import requests

# Os paths já são configurados pelo conftest.py raiz

# Configurações globais
TEST_CONFIG = {
    'BASE_URL': 'http://localhost:5000',
    'ADMIN_EMAIL': 'admin@restel.com',
    'ADMIN_PASSWORD': 'admin123',
    'HEADLESS': True,  # Mude para False para ver o browser
    'WAIT_TIMEOUT': 10,
    'DB_TIMEOUT': 30
}

def pytest_configure(config):
    """Configuração inicial do pytest"""
    # Registrar marcadores personalizados
    config.addinivalue_line("markers", "unit: Testes unitários básicos")
    config.addinivalue_line("markers", "integration: Testes de integração")
    config.addinivalue_line("markers", "e2e: Testes end-to-end com Selenium")
    config.addinivalue_line("markers", "api: Testes de API/rotas")
    config.addinivalue_line("markers", "smoke: Testes de fumaça (críticos)")
    config.addinivalue_line("markers", "regression: Testes de regressão")
    config.addinivalue_line("markers", "slow: Testes lentos")
    config.addinivalue_line("markers", "crud: Testes de CRUD")
    config.addinivalue_line("markers", "auth: Testes de autenticação")

# ============================================================================
# FIXTURES DE BANCO DE DADOS
# ============================================================================

@pytest.fixture(scope="session")
def test_database():
    """Cria banco de dados temporário para testes"""
    # Criar arquivo temporário
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    # Configurar aplicação com banco de teste
    os.environ['FLASK_TESTING'] = 'True'
    os.environ['TEST_DATABASE'] = temp_db.name
    
    # Importar e configurar app
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
    """Limpa dados do banco entre testes"""
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    
    # Limpar dados mas manter estrutura
    cursor.execute("DELETE FROM hospedes WHERE email != 'admin@restel.com'")
    cursor.execute("DELETE FROM administradores WHERE email != 'admin@restel.com'")
    
    conn.commit()
    conn.close()
    
    yield test_database

@pytest.fixture(scope="function") 
def app_client(test_database):
    """Cliente de teste Flask"""
    from app import app
    app.config['TESTING'] = True
    app.config['DATABASE'] = test_database
    
    with app.test_client() as client:
        with app.app_context():
            yield client

# ============================================================================
# FIXTURES DE SELENIUM
# ============================================================================

@pytest.fixture(scope="session")
def selenium_driver():
    """Driver Selenium configurado"""
    chrome_options = Options()
    
    if TEST_CONFIG['HEADLESS']:
        chrome_options.add_argument("--headless")
    
    # Opções para estabilidade
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Configurar service
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(TEST_CONFIG['WAIT_TIMEOUT'])
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="function")
def driver(selenium_driver):
    """Driver limpo para cada teste"""
    # Limpar cookies e cache
    selenium_driver.delete_all_cookies()
    
    yield selenium_driver

# ============================================================================
# FIXTURES DE APLICAÇÃO
# ============================================================================

@pytest.fixture(scope="session")
def flask_server(test_database):
    """Servidor Flask para testes E2E"""
    from app import app
    
    # Configurar app para testes
    app.config['TESTING'] = True
    app.config['DATABASE'] = test_database
    
    # Iniciar servidor em thread separada
    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Aguardar servidor iniciar
    max_attempts = 30
    for _ in range(max_attempts):
        try:
            response = requests.get(TEST_CONFIG['BASE_URL'])
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        pytest.fail("Servidor Flask não iniciou a tempo")
    
    yield TEST_CONFIG['BASE_URL']

# ============================================================================
# FIXTURES DE DADOS DE TESTE
# ============================================================================

@pytest.fixture
def sample_guest_data():
    """Dados de exemplo para hóspede"""
    return {
        'nome_completo': 'João Silva Teste',
        'email': 'joao.teste@email.com',
        'cpf': '12345678901',
        'telefone': '(11) 99999-8888',
        'senha': 'senha123'
    }

@pytest.fixture
def sample_admin_data():
    """Dados de exemplo para administrador"""
    return {
        'nome_completo': 'Admin Teste',
        'email': 'admin.teste@restel.com',
        'senha': 'admin123',
        'perfil': 'Padrão'
    }

@pytest.fixture
def admin_login_data():
    """Dados de login do admin"""
    return {
        'email': TEST_CONFIG['ADMIN_EMAIL'],
        'senha': TEST_CONFIG['ADMIN_PASSWORD']
    }

# ============================================================================
# FIXTURES DE PÁGINAS (PAGE OBJECTS)
# ============================================================================

@pytest.fixture
def admin_login_page(driver):
    """Página de login do admin"""
    from pages.admin_pages import AdminLoginPage
    return AdminLoginPage(driver)

@pytest.fixture
def admin_panel_page(driver):
    """Página do painel admin"""
    from pages.admin_pages import AdminPanelPage
    return AdminPanelPage(driver)

@pytest.fixture
def guest_pages(driver):
    """Páginas de hóspedes"""
    from pages.guest_pages import GuestPages
    return GuestPages(driver)

# ============================================================================
# FIXTURES UTILITÁRIAS
# ============================================================================

@pytest.fixture
def logged_admin_session(app_client, admin_login_data):
    """Sessão com admin logado"""
    response = app_client.post('/admin/login', data=admin_login_data)
    assert response.status_code in [200, 302]
    return app_client

@pytest.fixture
def screenshot_on_failure(request, driver):
    """Captura screenshot em caso de falha"""
    yield
    
    if request.node.rep_call.failed:
        # Criar diretório se não existir
        screenshot_dir = Path(__file__).parent.parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo
        test_name = request.node.nodeid.replace("::", "_").replace("/", "_")
        screenshot_path = screenshot_dir / f"FAILED_{test_name}.png"
        
        # Capturar screenshot
        driver.save_screenshot(str(screenshot_path))
        print(f"Screenshot salvo: {screenshot_path}")

# ============================================================================
# HOOKS PYTEST
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook para capturar resultados dos testes"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

def pytest_collection_modifyitems(config, items):
    """Modificar itens de teste coletados"""
    # Adicionar marcadores automáticos baseados na localização
    for item in items:
        # Adicionar marcador baseado no diretório
        if "unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "api/" in str(item.fspath):
            item.add_marker(pytest.mark.api)

# ============================================================================
# CONFIGURAÇÕES ADICIONAIS
# ============================================================================

# Configurar logging para testes
import logging
logging.basicConfig(level=logging.INFO)

# Desabilitar avisos desnecessários
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 