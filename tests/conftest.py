"""
Configurações globais para os testes automatizados do RESTEL
"""
import pytest
import time
import subprocess
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Tentativa de usar webdriver-manager, com fallback para ChromeDriver local
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class FlaskAppManager:
    """Gerenciador para iniciar e parar a aplicação Flask"""
    
    def __init__(self):
        self.process = None
        self.thread = None
    
    def start_app(self):
        """Inicia a aplicação Flask em thread separada"""
        def run_app():
            subprocess.run(['python', 'app.py'], cwd='.')
        
        self.thread = threading.Thread(target=run_app, daemon=True)
        self.thread.start()
        time.sleep(3)  # Aguarda a aplicação inicializar
    
    def stop_app(self):
        """Para a aplicação Flask"""
        if self.process:
            self.process.terminate()


@pytest.fixture(scope="session")
def flask_app():
    """Fixture para gerenciar a aplicação Flask durante os testes"""
    app_manager = FlaskAppManager()
    app_manager.start_app()
    yield app_manager
    app_manager.stop_app()


def get_chrome_driver_service():
    """Obtém o serviço do ChromeDriver de forma robusta"""
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            # Limpa cache antigo
            import tempfile
            import shutil
            cache_path = os.path.join(tempfile.gettempdir(), '.wdm')
            if os.path.exists(cache_path):
                try:
                    shutil.rmtree(cache_path)
                except:
                    pass
            
            # Tenta usar webdriver-manager
            driver_path = ChromeDriverManager().install()
            return Service(driver_path)
    except Exception as e:
        print(f"⚠️ Webdriver-manager falhou: {e}")
    
    # Fallback: busca ChromeDriver no sistema
    possible_paths = [
        "chromedriver.exe",
        "C:\\chromedriver\\chromedriver.exe",
        "C:\\Program Files\\ChromeDriver\\chromedriver.exe",
        "C:\\Program Files (x86)\\ChromeDriver\\chromedriver.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return Service(path)
    
    # Se nada funcionar, tenta sem especificar path
    return Service()


@pytest.fixture(scope="function")
def driver():
    """Fixture para configurar e fornecer o WebDriver"""
    # Configurações do Chrome
    chrome_options = Options()
    
    # Configurações para melhor compatibilidade no Windows
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Headless apenas se especificado
    if os.environ.get("PYTEST_BROWSER_HEADLESS", "true").lower() != "false":
        chrome_options.add_argument("--headless")
    
    # Obtém o serviço do Chrome
    service = get_chrome_driver_service()
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        driver.maximize_window()
        yield driver
    except Exception as e:
        print(f"❌ Erro ao inicializar Chrome: {e}")
        print("💡 Certifique-se que o Google Chrome está instalado")
        raise
    finally:
        try:
            driver.quit()
        except:
            pass


@pytest.fixture(scope="function")
def wait(driver):
    """Fixture para WebDriverWait"""
    return WebDriverWait(driver, 10)


@pytest.fixture(scope="function")
def admin_login(driver, wait):
    """Fixture para realizar login de administrador antes dos testes"""
    driver.get("http://localhost:5000/admin_login")
    
    # Preenche dados de login
    email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
    email_field.send_keys("admin@restel.com")
    
    password_field = driver.find_element(By.ID, "senha")
    password_field.send_keys("admin123")
    
    # Submete o formulário
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    
    # Aguarda redirecionamento para painel admin
    wait.until(EC.url_contains("/admin_painel"))
    
    return driver


# Dados de teste padronizados
@pytest.fixture
def guest_data():
    """Dados para teste de hóspedes"""
    return {
        "valid": {
            "nome": "João Silva",
            "email": "joao.silva@email.com",
            "telefone": "(11) 99999-9999",
            "cpf": "123.456.789-00",
            "endereco": "Rua das Flores, 123"
        },
        "invalid": {
            "nome": "",
            "email": "email_invalido",
            "telefone": "123",
            "cpf": "cpf_invalido",
            "endereco": ""
        },
        "update": {
            "nome": "João Silva Santos",
            "email": "joao.santos@email.com",
            "telefone": "(11) 88888-8888",
            "cpf": "123.456.789-00",
            "endereco": "Rua das Rosas, 456"
        }
    }


@pytest.fixture
def admin_data():
    """Dados para teste de administradores"""
    return {
        "valid": {
            "nome": "Maria Admin",
            "email": "maria.admin@restel.com",
            "senha": "senha123",
            "perfil": "Standard"
        },
        "invalid": {
            "nome": "",
            "email": "email_invalido",
            "senha": "123",
            "perfil": ""
        },
        "update": {
            "nome": "Maria Administradora",
            "email": "maria.admin@restel.com",
            "senha": "nova_senha123",
            "perfil": "Master"
        }
    } 