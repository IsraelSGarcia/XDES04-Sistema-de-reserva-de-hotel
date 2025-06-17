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

# Configurar PYTHONPATH para encontrar a aplicação
project_root = Path(__file__).parent.parent  # tests/conftest.py -> project root
app_path = project_root / "src" / "restel"

# Adicionar paths necessários
sys.path.insert(0, str(app_path))
sys.path.insert(0, str(project_root))

# Função para perguntar sobre modo de exibição do browser
def ask_browser_mode():
    """Pergunta ao usuário se quer ver o browser ou rodar em modo transparente"""
    print("\n" + "="*60)
    print("🌐 CONFIGURAÇÃO DO BROWSER PARA TESTES E2E")
    print("="*60)
    print("1. 👁️  Modo Visível - Ver o browser executando os testes")
    print("2. 🥷 Modo Transparente - Browser invisível (headless)")
    print("="*60)
    print("💡 Dica: Use --headless ou --visible para pular esta pergunta")
    print("="*60)
    
    while True:
        try:
            choice = input("Escolha uma opção (1 ou 2): ").strip()
            if choice == '1':
                print("✅ Modo selecionado: Browser VISÍVEL")
                return False  # Não headless
            elif choice == '2':
                print("✅ Modo selecionado: Browser TRANSPARENTE")
                return True   # Headless
            else:
                print("❌ Opção inválida! Digite 1 ou 2.")
        except (KeyboardInterrupt, EOFError):
            print("\n⏹️  Cancelado pelo usuário. Usando modo transparente por padrão.")
            return True

# Configurações globais otimizadas para performance
TEST_CONFIG = {
    'BASE_URL': 'http://localhost:5000',
    'ADMIN_EMAIL': 'admin@restel.com',
    'ADMIN_PASSWORD': 'admin123',
    'HEADLESS': True,  # Valor padrão, será atualizado dinamicamente
    'WAIT_TIMEOUT': 3,  # Reduzido de 10 para 3 segundos
    'PAGE_LOAD_TIMEOUT': 10,  # Reduzido de 30 para 10 segundos
    'SCRIPT_TIMEOUT': 5,  # Reduzido de 30 para 5 segundos
    'DB_TIMEOUT': 30
}

def pytest_addoption(parser):
    """Adiciona opções de linha de comando para pytest"""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Executar browser em modo headless (transparente)"
    )
    parser.addoption(
        "--visible",
        action="store_true", 
        default=False,
        help="Executar browser em modo visível"
    )

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
    print(f"[conftest.py test_database] Current sys.path[0]: {sys.path[0]}", flush=True)
    print(f"[conftest.py test_database] Current sys.path[1]: {sys.path[1]}", flush=True)
    print(f"[conftest.py test_database] project_root: {project_root}", flush=True)
    print(f"[conftest.py test_database] app_path: {app_path}", flush=True)
    import app as app_module
    print(f"[conftest.py test_database] Imported app_module from: {app_module.__file__}", flush=True)
    from app import app, init_db
    print(f"[conftest.py test_database] Imported app object: {app}", flush=True)
    
    # Override global DATABASE variable for tests
    app_module.DATABASE = temp_db.name
    app.config['TESTING'] = True
    app.config['DATABASE'] = temp_db.name
    
    # Inicializar banco
    with app.app_context():
        init_db()
    
    # Conectar ao banco de dados temporário
    conn = None
    try:
        conn = sqlite3.connect(temp_db.name, timeout=TEST_CONFIG.get('DB_TIMEOUT', 30))
        conn.row_factory = sqlite3.Row # Para acesso por nome de coluna
        yield conn # Fornece a conexão para os testes
    finally:
        if conn:
            conn.close()
        # Cleanup - ensure all connections are closed (original cleanup for file deletion)
    try:
        os.unlink(temp_db.name)
    except PermissionError:
        # On Windows, try to force close connections
        import gc
        gc.collect()
        try:
            os.unlink(temp_db.name)
        except PermissionError:
            pass  # File will be cleaned up by system later

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
def selenium_driver(request):
    """Driver Selenium configurado"""
    # Determinar modo do browser
    headless_mode = True  # Padrão
    
    # Verificar argumentos de linha de comando
    if hasattr(request.config.option, 'visible') and request.config.option.visible:
        headless_mode = False
        print("🖥️  Modo VISÍVEL ativado via --visible")
    elif hasattr(request.config.option, 'headless') and request.config.option.headless:
        headless_mode = True
        print("🥷 Modo TRANSPARENTE ativado via --headless")
    else:
        # Se não há argumentos específicos, perguntar ao usuário
        headless_mode = ask_browser_mode()
    
    # Atualizar configuração global
    TEST_CONFIG['HEADLESS'] = headless_mode
    
    chrome_options = Options()
    
    # Configurações básicas otimizadas para velocidade
    if headless_mode:
        chrome_options.add_argument("--headless=new")
        print("🚀 Modo TURBO TRANSPARENTE ativado")
    else:
        print("🖥️  Modo VISÍVEL ativado")
    
    # Configurações essenciais e rápidas
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1366,768")  # Tamanho menor = mais rápido
    
    # Otimizações agressivas para velocidade
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Sempre desabilitar imagens
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows") 
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
    chrome_options.add_argument("--aggressive-cache-discard")
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    
    # Suprimir logs para velocidade
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Prefs para velocidade máxima
    prefs = {
        "profile.default_content_setting_values": {
            "images": 2,  # Bloquear imagens
            "plugins": 2,  # Bloquear plugins
            "popups": 2,   # Bloquear popups
            "geolocation": 2,  # Bloquear localização
            "notifications": 2,  # Bloquear notificações
            "media_stream": 2  # Bloquear media
        },
        "profile.managed_default_content_settings": {
            "images": 2
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # ChromeDriver otimizado para velocidade
    try:
        # Cache do driver para evitar downloads repetidos  
        service = Service(
            ChromeDriverManager().install(),
            log_path=os.devnull
        )
    except Exception:
        service = Service(log_path=os.devnull)
    
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Timeouts otimizados para velocidade
        driver.implicitly_wait(TEST_CONFIG['WAIT_TIMEOUT'])  # 3 segundos
        driver.set_page_load_timeout(TEST_CONFIG['PAGE_LOAD_TIMEOUT'])  # 10 segundos
        driver.set_script_timeout(TEST_CONFIG['SCRIPT_TIMEOUT'])  # 5 segundos
        
        print(f"⚡ Browser iniciado em modo TURBO (timeouts: {TEST_CONFIG['WAIT_TIMEOUT']}s)")
        
        yield driver
        
    except Exception as e:
        print(f"Erro ao inicializar driver: {e}")
        if driver:
            driver.quit()
        raise
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass  # Ignorar erros ao fechar

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
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilitar CSRF nos testes
    
    # Suprimir logs do Flask
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Iniciar servidor em thread separada
    server_thread = threading.Thread(
        target=lambda: app.run(
            port=5000, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Aguardar servidor iniciar - otimizado para velocidade
    max_attempts = 10  # Reduzido de 30 para 10
    for attempt in range(max_attempts):
        try:
            response = requests.get(TEST_CONFIG['BASE_URL'], timeout=2)  # Timeout reduzido
            if response.status_code == 200:
                print(f"⚡ Servidor Flask iniciado em {attempt + 1} tentativas")
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < max_attempts - 1:
                time.sleep(0.5)  # Reduzido de 1s para 0.5s
    else:
        pytest.fail("Servidor Flask não iniciou a tempo")
    
    yield TEST_CONFIG['BASE_URL']

# ============================================================================  
# IMPORT FIXTURES FROM OTHER MODULES
# ============================================================================

# Import fixtures from auth_fixtures
from tests.fixtures.auth_fixtures import (
    admin_credentials, 
    guest_credentials, 
    logged_admin_client, 
    logged_guest_client, 
    invalid_credentials
)

# Import fixtures from data_fixtures  
from tests.fixtures.data_fixtures import (
    valid_guest_data,
    invalid_guest_data, 
    valid_admin_data,
    invalid_admin_data,
    random_guest_data,
    multiple_guests_data,
    edge_case_data,
    sql_injection_data,
    bulk_test_data
)

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