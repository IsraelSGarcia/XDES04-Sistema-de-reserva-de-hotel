#!/usr/bin/env python3
"""
Script para execução dos testes automatizados do RESTEL
"""
import os
import sys
import subprocess
import argparse
import webbrowser
from datetime import datetime


def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import selenium
        import pytest
        import webdriver_manager
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("Execute: pip install -r requirements.txt")
        return False


def check_flask_app():
    """Verifica se a aplicação Flask está rodando"""
    import requests
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicação Flask está rodando")
            return True
    except:
        pass
    
    print("❌ Aplicação Flask não está rodando")
    print("Execute em outro terminal: python app.py")
    return False


def install_dependencies():
    """Instala dependências necessárias"""
    print("📦 Instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False


def create_directories():
    """Cria diretórios necessários para os testes"""
    directories = [
        "tests/screenshots",
        "tests/reports"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Diretório criado: {directory}")


def run_tests(test_type="all", browser="chrome", headless=True, generate_report=True):
    """Executa os testes automatizados"""
    
    # Argumentos base do pytest
    pytest_args = [
        "-v",  # verbose
        "--tb=short",  # traceback curto
        "--color=yes"  # cores no output
    ]
    
    # Configuração do browser
    if not headless:
        os.environ["PYTEST_BROWSER_HEADLESS"] = "false"
    
    # Relatório HTML
    if generate_report:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/reports/report_{timestamp}.html"
        pytest_args.extend([
            "--html", report_file,
            "--self-contained-html"
        ])
        print(f"📊 Relatório será gerado em: {report_file}")
    
    # Seleção de testes por tipo
    if test_type == "guest":
        pytest_args.append("tests/test_guest_crud.py")
    elif test_type == "admin":
        pytest_args.append("tests/test_admin_crud.py")
    elif test_type == "login":
        pytest_args.extend(["-m", "login"])
    elif test_type == "smoke":
        pytest_args.extend(["-m", "smoke"])
    else:  # all
        pytest_args.append("tests/")
    
    print(f"\n🚀 Executando testes: {test_type}")
    print(f"🌐 Browser: {browser} (headless: {headless})")
    print("="*60)
    
    try:
        # Executa os testes
        result = subprocess.run([sys.executable, "-m", "pytest"] + pytest_args, 
                              capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ Todos os testes passaram!")
            
            # Abre relatório no browser se foi gerado
            if generate_report and 'report_file' in locals():
                print(f"🌐 Abrindo relatório no browser...")
                webbrowser.open(f"file://{os.path.abspath(report_file)}")
        else:
            print(f"\n❌ Alguns testes falharam (código: {result.returncode})")
            
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução dos testes interrompida pelo usuário")
        return False
    except Exception as e:
        print(f"\n💥 Erro ao executar testes: {e}")
        return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executa testes automatizados do RESTEL")
    
    parser.add_argument(
        "--type", 
        choices=["all", "guest", "admin", "login", "smoke"],
        default="all",
        help="Tipo de testes para executar (padrão: all)"
    )
    
    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox"],
        default="chrome",
        help="Browser para usar nos testes (padrão: chrome)"
    )
    
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Executa testes com browser visível (não headless)"
    )
    
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Não gera relatório HTML"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Instala dependências antes de executar"
    )
    
    parser.add_argument(
        "--check-flask",
        action="store_true",
        help="Verifica se Flask está rodando antes de executar"
    )
    
    args = parser.parse_args()
    
    print("🏨 RESTEL - Sistema de Testes Automatizados")
    print("="*50)
    
    # Instala dependências se solicitado
    if args.install_deps:
        if not install_dependencies():
            return 1
    
    # Verifica dependências
    if not check_dependencies():
        return 1
    
    # Verifica se Flask está rodando se solicitado
    if args.check_flask:
        if not check_flask_app():
            return 1
    
    # Cria diretórios necessários
    create_directories()
    
    # Executa os testes
    success = run_tests(
        test_type=args.type,
        browser=args.browser,
        headless=not args.visible,
        generate_report=not args.no_report
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 