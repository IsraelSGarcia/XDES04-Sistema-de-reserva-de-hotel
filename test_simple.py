#!/usr/bin/env python3
"""
Teste simples para verificar se Selenium + Flask funcionam
"""
import time
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_flask():
    """Inicia Flask em background"""
    def run_flask():
        subprocess.run(['python', 'app.py'], capture_output=True)
    
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    print("🚀 Flask iniciado em background...")
    time.sleep(3)  # Aguarda inicializar

def test_selenium_chrome():
    """Testa se Selenium funciona"""
    print("🧪 Testando Selenium + Chrome...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        print(f"✅ Selenium OK - Título: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Erro no Selenium: {e}")
        return False

def test_flask_connection():
    """Testa se consegue conectar no Flask"""
    print("🌐 Testando conexão com Flask...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("http://localhost:5000")
        
        # Verifica se a página carregou
        wait = WebDriverWait(driver, 10)
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print(f"✅ Flask OK - Título: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar no Flask: {e}")
        return False

def main():
    print("🏨 RESTEL - Teste Simples")
    print("=" * 40)
    
    # Teste 1: Selenium
    if not test_selenium_chrome():
        print("❌ Falha no teste do Selenium")
        return
    
    # Teste 2: Flask
    start_flask()
    
    # Teste 3: Conexão Flask
    if test_flask_connection():
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("🎉 Sistema pronto para testes automatizados!")
    else:
        print("\n❌ Falha na conexão com Flask")
        print("💡 Certifique-se que app.py está funcionando")

if __name__ == "__main__":
    main() 