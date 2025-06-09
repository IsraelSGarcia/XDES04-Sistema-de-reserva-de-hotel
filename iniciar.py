#!/usr/bin/env python3
"""
🏨 RESTEL - Script de Inicialização Principal
Sistema de Gestão Hoteleira

Este script fornece acesso rápido a todas as funcionalidades do sistema.
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Exibe o banner principal do sistema"""
    print("=" * 60)
    print("  🏨 RESTEL - SISTEMA DE GESTÃO HOTELEIRA")
    print("=" * 60)
    print("  📍 Hotel Boa Estadia")
    print("  🏢 SWFactory Consultoria e Sistemas Ltda")
    print("=" * 60)
    print()

def print_menu():
    """Exibe o menu principal"""
    print("🚀 Opções Disponíveis:")
    print()
    print("  1. ⚙️  Configurar Ambiente de Desenvolvimento")
    print("  2. 🧪 Executar Testes (Interface Interativa)")
    print("  3. 🌐 Iniciar Aplicação Web")
    print("  4. 📊 Ver Status do Projeto")
    print("  5. 📚 Abrir Documentação")
    print("  6. 🔧 Ferramentas de Desenvolvimento")
    print("  0. 🚪 Sair")
    print()

def run_setup():
    """Executa configuração do ambiente"""
    print("⚙️  Executando configuração do ambiente...")
    os.system('python tools/setup_dev.py')

def run_tests():
    """Executa interface de testes"""
    print("🧪 Abrindo executor de testes...")
    os.system('python tools/test_runner.py')

def start_app():
    """Inicia a aplicação web"""
    print("🌐 Iniciando aplicação web...")
    print("📍 Acesse: http://localhost:5000")
    print("👤 Admin: admin@restel.com / admin123")
    print()
    os.system('python src/restel/app.py')

def show_status():
    """Mostra status do projeto"""
    print("📊 Status do Projeto RESTEL:")
    print()
    
    # Verificar estrutura
    required_dirs = ['src/restel', 'tests', 'data', 'tools', 'docs']
    print("📁 Estrutura de Diretórios:")
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✅ {dir_name}")
        else:
            print(f"  ❌ {dir_name} (ausente)")
    
    print()
    
    # Verificar arquivos principais
    required_files = [
        'src/restel/app.py',
        'tools/setup_dev.py', 
        'tools/test_runner.py',
        'requirements.txt',
        'README.md'
    ]
    print("📄 Arquivos Principais:")
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} (ausente)")
    
    print()
    
    # Verificar banco
    if Path('data/restel.db').exists():
        print("  ✅ Banco de dados: data/restel.db")
    else:
        print("  ⚠️  Banco de dados não encontrado (execute configuração)")
    
    print()
    input("Pressione Enter para continuar...")

def show_docs():
    """Mostra documentação disponível"""
    print("📚 Documentação Disponível:")
    print()
    print("  📖 README.md - Documentação principal")
    print("  🛠️  docs/DESENVOLVIMENTO.md - Guia técnico")
    print("  📋 docs/CLEANUP_PLAN.md - Histórico de organização")
    print("  🧪 tests/README.md - Documentação de testes")
    print()
    
    choice = input("Deseja abrir algum arquivo? (1-4, 0=voltar): ").strip()
    
    if choice == '1':
        os.system('notepad README.md' if os.name == 'nt' else 'cat README.md')
    elif choice == '2':
        os.system('notepad docs/DESENVOLVIMENTO.md' if os.name == 'nt' else 'cat docs/DESENVOLVIMENTO.md')
    elif choice == '3':
        os.system('notepad docs/CLEANUP_PLAN.md' if os.name == 'nt' else 'cat docs/CLEANUP_PLAN.md')
    elif choice == '4':
        os.system('notepad tests/README.md' if os.name == 'nt' else 'cat tests/README.md')

def show_tools():
    """Mostra ferramentas de desenvolvimento"""
    print("🔧 Ferramentas de Desenvolvimento:")
    print()
    print("  1. 🗃️  Reinicializar Banco de Dados")
    print("  2. 🧹 Limpar Cache e Arquivos Temporários")
    print("  3. 📊 Gerar Relatório de Testes")
    print("  4. 🔄 Atualizar Dependências")
    print("  0. ↩️  Voltar")
    print()
    
    choice = input("Selecione uma ferramenta (0-4): ").strip()
    
    if choice == '1':
        print("🗃️  Reinicializando banco de dados...")
        if Path('data/restel.db').exists():
            os.remove('data/restel.db')
        os.system('python src/restel/app.py')
        print("✅ Banco reinicializado!")
        
    elif choice == '2':
        print("🧹 Limpando cache...")
        os.system('python tools/test_runner.py' if Path('tools/test_runner.py').exists() else 'echo "Test runner não encontrado"')
        
    elif choice == '3':
        print("📊 Gerando relatório...")
        os.system('pytest tests/ --html=tests/reports/report.html --self-contained-html')
        print("✅ Relatório gerado em: tests/reports/report.html")
        
    elif choice == '4':
        print("🔄 Atualizando dependências...")
        os.system('pip install -r requirements.txt --upgrade')
    
    input("\nPressione Enter para continuar...")

def main():
    """Loop principal do programa"""
    while True:
        print_banner()
        show_status()
        print_menu()
        
        try:
            choice = input("🎯 Selecione uma opção (0-6): ").strip()
            print()
            
            if choice == '0':
                print("👋 Obrigado por usar o RESTEL!")
                print("🏨 Sistema de Gestão Hoteleira")
                break
                
            elif choice == '1':
                run_setup()
                
            elif choice == '2':
                run_tests()
                
            elif choice == '3':
                start_app()
                
            elif choice == '4':
                show_status()
                
            elif choice == '5':
                show_docs()
                
            elif choice == '6':
                show_tools()
                
            else:
                print("❌ Opção inválida. Escolha entre 0-6.")
                input("Pressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"💥 Erro: {e}")
            input("Pressione Enter para continuar...")

if __name__ == '__main__':
    main() 