#!/usr/bin/env python3
"""
Teste das rotas do RESTEL para verificar se estão corretas
"""
import time
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_flask():
    """Inicia Flask em background"""
    def run_flask():
        subprocess.run(['python', 'app.py'], capture_output=True)
    
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    print("🚀 Flask iniciado em background...")
    time.sleep(3)  # Aguarda inicializar

def test_routes():
    """Testa se as rotas principais estão funcionando"""
    print("🔗 Testando rotas principais...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    routes_to_test = [
        ("Página Inicial", "http://localhost:5000/"),
        ("Login Admin", "http://localhost:5000/admin/login"),
        ("Cadastro Hóspede", "http://localhost:5000/hospede/cadastro")
    ]
    
    try:
        driver = webdriver.Chrome(options=options)
        
        for name, url in routes_to_test:
            try:
                print(f"  🌐 Testando: {name} ({url})")
                driver.get(url)
                
                # Aguarda página carregar
                wait = WebDriverWait(driver, 10)
                body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Verifica se não é página de erro 404/500
                page_source = driver.page_source.lower()
                if "404" in page_source or "not found" in page_source or "error" in page_source:
                    print(f"    ❌ ERRO: Página retornou erro")
                    return False
                
                print(f"    ✅ OK - Título: {driver.title}")
                
            except Exception as e:
                print(f"    ❌ FALHA: {e}")
                return False
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_admin_login():
    """Testa se consegue fazer login de admin"""
    print("🔐 Testando login de administrador...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("http://localhost:5000/admin/login")
        
        # Aguarda e preenche formulário
        wait = WebDriverWait(driver, 10)
        
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys("admin@restel.com")
        
        password_field = driver.find_element(By.ID, "senha")
        password_field.send_keys("admin123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verifica se redirecionou para painel
        time.sleep(2)
        current_url = driver.current_url
        
        if "/admin/painel" in current_url:
            print("  ✅ Login bem-sucedido - Redirecionou para painel")
            driver.quit()
            return True
        else:
            print(f"  ❌ Login falhou - URL atual: {current_url}")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"  ❌ Erro no login: {e}")
        return False

def main():
    print("🏨 RESTEL - Teste de Rotas")
    print("=" * 40)
    
    # Inicia Flask
    start_flask()
    
    # Testa rotas
    if not test_routes():
        print("\n❌ Falha no teste de rotas")
        return
    
    # Testa login
    if test_admin_login():
        print("\n✅ TODOS OS TESTES DE ROTA PASSARAM!")
        print("🎉 Sistema pronto para testes automatizados!")
    else:
        print("\n❌ Falha no teste de login")

if __name__ == "__main__":
    main() 