#!/usr/bin/env python3
"""
Script simples para executar testes com menos erros
"""
import sys
import os
import subprocess
import logging
from pathlib import Path

# Configurar logging para suprimir mensagens desnecessárias
logging.basicConfig(level=logging.ERROR)

def setup_environment():
    """Configura o ambiente para os testes"""
    # Adiciona o diretório raiz ao PYTHONPATH
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Configurar variáveis de ambiente para reduzir ruído
    os.environ['PYTHONWARNINGS'] = 'ignore'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['SELENIUM_LOG_LEVEL'] = '3'
    
def run_simple_test():
    """Executa um teste simples primeiro"""
    cmd = [
        sys.executable, '-m', 'pytest', 
        'tests/unit/test_simple.py',
        '-v', '--tb=short', '--disable-warnings', '-q'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Teste simples passou!")
            return True
        else:
            print("❌ Teste simples falhou:")
            print(result.stdout)
            if result.stderr:
                print("Erros:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Teste simples expirou")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False

def run_admin_crud_test():
    """Executa o teste de CRUD de admin"""
    cmd = [
        sys.executable, '-m', 'pytest', 
        'tests/e2e/test_admin_crud.py::TestAdminCRUD::test_admin_login_valid_credentials',
        '-v', '--tb=short', '--disable-warnings', '-q', '--maxfail=1'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)        if result.returncode == 0:
            print("✅ Teste de login admin passou!")
            return True
        else:
            print("❌ Teste de login admin falhou:")
            print(result.stdout)
            if result.stderr:
                print("Erros:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Teste de login admin expirou")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False

def run_guest_crud_test():
    """Executa o teste de CRUD de hóspede"""
    cmd = [
        sys.executable, '-m', 'pytest', 
        'tests/e2e/test_guest_crud.py::TestGuestCRUD::test_create_guest_valid_data',
        '-v', '--tb=short', '--disable-warnings', '-q', '--maxfail=1'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Teste de criação de hóspede passou!")
            return True
        else:
            print("❌ Teste de criação de hóspede falhou:")
            print(result.stdout)
            if result.stderr:
                print("Erros:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Teste de criação de hóspede expirou")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes com configuração simplificada...")
    
    setup_environment()
    
    # Executar teste simples primeiro
    print("\n1️⃣ Executando teste simples...")
    if not run_simple_test():
        print("❌ Teste simples falhou. Verifique a configuração básica.")
        return 1
    
    # Executar teste de admin
    print("\n2️⃣ Executando teste de admin...")
    if not run_admin_crud_test():
        print("❌ Teste de admin falhou.")
        return 1
    
    # Executar teste de hóspede
    print("\n3️⃣ Executando teste de hóspede...")
    if not run_guest_crud_test():
        print("❌ Teste de hóspede falhou.")
        return 1
    
    print("\n✅ Todos os testes básicos passaram!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
