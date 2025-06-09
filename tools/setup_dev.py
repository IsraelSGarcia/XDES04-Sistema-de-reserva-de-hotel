#!/usr/bin/env python3
"""
Script de Configuração de Desenvolvimento para o Sistema RESTEL
Inicializa o ambiente do projeto e banco de dados
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_banner():
    """Exibe o banner de configuração"""
    print("=" * 60)
    print("  🏨 RESTEL GESTÃO HOTELEIRA - CONFIGURAÇÃO DEV")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 ou superior é necessário")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def install_dependencies():
    """Instala os pacotes Python necessários"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Falha ao instalar dependências")
        return False

def create_directories():
    """Cria os diretórios necessários"""
    print("📁 Criando estrutura de diretórios...")
    
    directories = [
        'data',
        'static/css',
        'static/js',
        'static/images',
        'tests/reports',
        'tests/screenshots',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  📂 {directory}")
    
    print("✅ Diretórios criados")

def initialize_database():
    """Inicializa o banco de dados"""
    print("🗃️  Inicializando banco de dados...")
    
    try:
        # Adiciona o caminho correto e importa a função de inicialização
        import sys
        from pathlib import Path
        app_path = Path(__file__).parent / 'src' / 'restel'
        sys.path.insert(0, str(app_path))
        
        from app import init_db
        init_db()
        print("✅ Banco de dados inicializado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Falha ao inicializar banco de dados: {e}")
        print("💡 Dica: Execute manualmente 'python src/restel/app.py' para criar o banco")
        return False

def create_gitignore():
    """Cria arquivo .gitignore"""
    print("📝 Criando .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Ambiente Virtual
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testes
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache

# Banco de dados
*.db-journal

# Logs
logs/
*.log

# Sistema Operacional
.DS_Store
Thumbs.db

# Relatórios
tests/reports/*.html
tests/screenshots/*.png
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore criado")

def run_tests():
    """Executa testes iniciais para verificar a configuração"""
    print("🧪 Executando testes iniciais...")
    
    try:
        result = subprocess.run(['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Todos os testes passaram!")
        else:
            print("⚠️  Alguns testes falharam, mas a configuração está completa")
            print("   Você pode executar testes individualmente para depurar")
        
        return True
    except FileNotFoundError:
        print("⚠️  pytest não encontrado. Instale com: pip install pytest")
        return False

def main():
    """Função principal de configuração"""
    print_banner()
    
    print("🚀 Iniciando configuração do ambiente de desenvolvimento...")
    print()
    
    # Verificar versão do Python
    if not check_python_version():
        sys.exit(1)
    
    # Instalar dependências
    if not install_dependencies():
        print("⚠️  Continuando configuração sem dependências...")
    
    # Criar diretórios
    create_directories()
    
    # Inicializar banco de dados
    if not initialize_database():
        print("⚠️  Falha na inicialização do banco. Você pode precisar executar manualmente.")
    
    # Criar .gitignore
    create_gitignore()
    
    # Executar testes
    run_tests()
    
    print()
    print("🎉 Configuração completa!")
    print()
    print("📋 Próximos passos:")
    print("  1. Execute a aplicação: python src/restel/app.py")
    print("  2. Execute os testes: python test_runner.py")
    print("  3. Acesse o painel admin: http://localhost:5000/admin/login")
    print("     Credenciais padrão: admin@restel.com / admin123")
    print()

if __name__ == '__main__':
    main() 