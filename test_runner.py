#!/usr/bin/env python3
"""
Executor de Testes Interativo para o Sistema RESTEL de Gestão Hoteleira
Fornece um menu fácil de usar para executar diferentes tipos de testes
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Exibe o banner do executor de testes"""
    print("=" * 60)
    print("  🏨 RESTEL GESTÃO HOTELEIRA - EXECUTOR DE TESTES")
    print("=" * 60)
    print()

def print_menu():
    """Exibe as opções do menu principal"""
    print("📋 Opções de Teste:")
    print("  1. 🚀 Executar Todos os Testes")
    print("  2. 🧪 Apenas Testes Unitários")
    print("  3. 🔗 Testes de Integração")
    print("  4. 👤 Testes CRUD de Hóspedes")
    print("  5. 🔐 Testes CRUD de Administradores")
    print("  6. 🌐 Testes de Rotas")
    print("  7. 📊 Gerar Relatório HTML")
    print("  8. 🧹 Limpar Cache de Testes")
    print("  9. ❓ Ajuda e Informações de Teste")
    print("  0. 🚪 Sair")
    print()

def run_command(cmd, description):
    """Executa um comando e mostra os resultados"""
    print(f"🔄 {description}...")
    print(f"💻 Comando: {cmd}")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=get_project_root())
        
        if result.stdout:
            print("📤 Saída:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Erros/Avisos:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Sucesso!")
        else:
            print(f"❌ Falhou com código de saída: {result.returncode}")
        
    except Exception as e:
        print(f"💥 Erro ao executar comando: {e}")
    
    print("-" * 40)
    input("Pressione Enter para continuar...")
    print()

def get_project_root():
    """Obtém o diretório raiz do projeto"""
    return Path(__file__).parent

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    project_root = get_project_root()
    
    # Verifica se os diretórios necessários existem
    required_dirs = ['tests', 'src/restel', 'data']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"⚠️  Aviso: Diretórios ausentes: {', '.join(missing_dirs)}")
    
    # Verifica se pytest está instalado
    try:
        subprocess.run(['pytest', '--version'], capture_output=True, check=True)
        print("✅ pytest está instalado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest não está instalado. Execute: pip install pytest")
        return False
    
    return True

def show_test_info():
    """Mostra informações sobre os testes disponíveis"""
    print("📖 Informações de Teste:")
    print()
    print("🔍 Arquivos de Teste Disponíveis:")
    
    tests_dir = get_project_root() / 'tests'
    if tests_dir.exists():
        test_files = list(tests_dir.glob('test_*.py'))
        for test_file in test_files:
            print(f"  📄 {test_file.name}")
    
    print()
    print("📊 Categorias de Teste:")
    print("  • Testes Unitários: Testes de funcionalidade básica")
    print("  • Testes de Integração: Testes de fluxo completo")
    print("  • Testes CRUD: Operações de Criar, Ler, Atualizar, Deletar")
    print("  • Testes de Rota: Testes de endpoints da API")
    print()
    print("🛠️  Configuração de Testes:")
    print("  • Arquivo de config: pytest.ini")
    print("  • Fixtures de teste: tests/conftest.py")
    print("  • Relatórios: tests/reports/")
    print()
    
    input("Pressione Enter para continuar...")

def main():
    """Loop principal do executor de testes"""
    # Muda para o diretório do projeto
    os.chdir(get_project_root())
    
    while True:
        print_banner()
        
        if not check_environment():
            print("❌ Verificação do ambiente falhou. Por favor, corrija os problemas acima.")
            sys.exit(1)
        
        print_menu()
        
        try:
            choice = input("🎯 Selecione uma opção (0-9): ").strip()
            print()
            
            if choice == '0':
                print("👋 Até logo!")
                break
            
            elif choice == '1':
                run_command('pytest tests/ -v --tb=short', 'Executando Todos os Testes')
            
            elif choice == '2':
                run_command('pytest tests/test_simple.py -v', 'Executando Testes Unitários')
            
            elif choice == '3':
                run_command('pytest tests/test_routes.py -v', 'Executando Testes de Integração')
            
            elif choice == '4':
                run_command('pytest tests/test_guest_crud.py -v', 'Executando Testes CRUD de Hóspedes')
            
            elif choice == '5':
                run_command('pytest tests/test_admin_crud.py -v', 'Executando Testes CRUD de Administradores')
            
            elif choice == '6':
                run_command('pytest tests/test_routes.py -v', 'Executando Testes de Rotas')
            
            elif choice == '7':
                run_command('pytest tests/ --html=tests/reports/report.html --self-contained-html -v', 
                          'Gerando Relatório HTML')
                print("📊 Relatório gerado em: tests/reports/report.html")
            
            elif choice == '8':
                run_command('pytest --cache-clear', 'Limpando Cache de Testes')
                # Também limpa diretórios __pycache__
                for pycache in Path('.').rglob('__pycache__'):
                    if pycache.is_dir():
                        import shutil
                        shutil.rmtree(pycache)
                        print(f"🗑️  Removido: {pycache}")
            
            elif choice == '9':
                show_test_info()
            
            else:
                print("❌ Opção inválida. Por favor, escolha 0-9.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"💥 Erro inesperado: {e}")
            time.sleep(2)

if __name__ == '__main__':
    main() 