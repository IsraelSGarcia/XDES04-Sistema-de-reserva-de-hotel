#!/usr/bin/env python3
"""
Sistema de Execução de Testes RESTEL

Execute: python tools/test_runner.py
"""

import subprocess
import sys
import os
from pathlib import Path


class TestRunner:
    """Sistema de execução de testes organizados"""
    
    def __init__(self):
        # Definir diretório base
        self.base_dir = Path(__file__).parent.parent
        
        # Comandos pytest básicos
        self.pytest_base = [
            sys.executable, "-m", "pytest",
            "-v",  # verbose
            "--tb=short",  # traceback curto
            "--strict-markers",  # marcadores obrigatórios
        ]
    
    def run_command(self, cmd, description=""):
        """Executa comando e mostra resultado"""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
        print(f"Comando: {' '.join(cmd)}")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n✅ {description} - SUCESSO")
            else:
                print(f"\n❌ {description} - FALHA (código: {result.returncode})")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Erro ao executar comando: {e}")
            return False
    
    def show_menu(self):
        """Mostra menu de opções"""
        print("\n" + "="*60)
        print("🧪 SISTEMA DE TESTES RESTEL")
        print("="*60)
        print()
        print("📂 EXECUÇÃO POR CATEGORIA:")
        print("1. Testes Unitários (tests/unit/)")
        print("2. Testes de Integração (tests/integration/)")
        print("3. Testes End-to-End (tests/e2e/)")
        print("4. Testes de API (tests/api/)")
        print()
        print("🏷️  EXECUÇÃO POR MARCADOR:")
        print("5. Testes Rápidos (-m smoke)")
        print("6. Testes Completos (-m 'not slow')")
        print("7. Testes de Banco (-m database)")
        print("8. Testes de Autenticação (-m auth)")
        print()
        print("⚙️  EXECUÇÃO PERSONALIZADA:")
        print("9. Executar arquivo específico")
        print("10. Executar com cobertura")
        print("11. Executar todos os testes")
        print()
        print("🛠️  FERRAMENTAS:")
        print("12. Gerar relatório HTML")
        print("13. Limpar cache de testes")
        print("14. Verificar configuração")
        print("15. Listar todos os testes")
        print("16. Ajuda/Documentação")
        print()
        print("0. Sair")
        print("="*60)
    
    def run_unit_tests(self):
        """Executa testes unitários"""
        cmd = self.pytest_base + ["tests/unit/"]
        return self.run_command(cmd, "Testes Unitários")
    
    def run_integration_tests(self):
        """Executa testes de integração"""
        cmd = self.pytest_base + ["tests/integration/"]
        return self.run_command(cmd, "Testes de Integração")
    
    def run_e2e_tests(self):
        """Executa testes end-to-end"""
        cmd = self.pytest_base + ["tests/e2e/"]
        return self.run_command(cmd, "Testes End-to-End")
    
    def run_api_tests(self):
        """Executa testes de API"""
        cmd = self.pytest_base + ["tests/api/"]
        return self.run_command(cmd, "Testes de API")
    
    def run_smoke_tests(self):
        """Executa testes de smoke"""
        cmd = self.pytest_base + ["-m", "smoke", "tests/"]
        return self.run_command(cmd, "Testes Smoke (Rápidos)")
    
    def run_full_tests(self):
        """Executa testes completos (exceto lentos)"""
        cmd = self.pytest_base + ["-m", "not slow", "tests/"]
        return self.run_command(cmd, "Testes Completos")
    
    def run_database_tests(self):
        """Executa testes de banco"""
        cmd = self.pytest_base + ["-m", "database", "tests/"]
        return self.run_command(cmd, "Testes de Banco de Dados")
    
    def run_auth_tests(self):
        """Executa testes de autenticação"""
        cmd = self.pytest_base + ["-m", "auth", "tests/"]
        return self.run_command(cmd, "Testes de Autenticação")
    
    def run_specific_file(self):
        """Executa arquivo específico"""
        file_path = input("Digite o caminho do arquivo de teste: ").strip()
        if not file_path:
            print("❌ Caminho não fornecido")
            return False
        
        cmd = self.pytest_base + [file_path]
        return self.run_command(cmd, f"Arquivo: {file_path}")
    
    def run_with_coverage(self):
        """Executa com cobertura"""
        cmd = self.pytest_base + [
            "--cov=src/restel",
            "--cov-report=html",
            "--cov-report=term",
            "tests/"
        ]
        return self.run_command(cmd, "Testes com Cobertura")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        cmd = self.pytest_base + ["tests/"]
        return self.run_command(cmd, "Todos os Testes")
    
    def generate_html_report(self):
        """Gera relatório HTML"""
        cmd = self.pytest_base + [
            "--html=reports/test_report.html",
            "--self-contained-html",
            "tests/"
        ]
        return self.run_command(cmd, "Relatório HTML")
    
    def clean_cache(self):
        """Limpa cache de testes"""
        cache_dirs = [
            self.base_dir / ".pytest_cache",
            self.base_dir / "__pycache__",
            self.base_dir / "tests" / "__pycache__"
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                print(f"✅ Removido: {cache_dir}")
        
        print("✅ Cache limpo com sucesso")
        return True
    
    def check_configuration(self):
        """Verifica configuração"""
        print("🔍 Verificando configuração...")
        
        # Verificar arquivos essenciais
        files_to_check = [
            "pytest.ini",
            "tests/conftest.py",
            "requirements.txt"
        ]
        
        for file_path in files_to_check:
            full_path = self.base_dir / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} (não encontrado)")
        
        # Verificar se pytest funciona
        cmd = [sys.executable, "-m", "pytest", "--version"]
        return self.run_command(cmd, "Verificação do pytest")
    
    def list_tests(self):
        """Lista todos os testes"""
        cmd = self.pytest_base + ["--collect-only", "-q", "tests/"]
        return self.run_command(cmd, "Lista de Testes")
    
    def show_help(self):
        """Mostra ajuda"""
        print("\n" + "="*60)
        print("📖 AJUDA - SISTEMA DE TESTES RESTEL")
        print("="*60)
        print()
        print("📁 ESTRUTURA DE TESTES:")
        print("  tests/unit/         - Testes unitários rápidos")
        print("  tests/integration/  - Testes de integração")
        print("  tests/e2e/         - Testes end-to-end")
        print("  tests/api/         - Testes de API/rotas")
        print()
        print("🏷️  MARCADORES DISPONÍVEIS:")
        print("  @pytest.mark.unit       - Teste unitário")
        print("  @pytest.mark.integration - Teste de integração")
        print("  @pytest.mark.e2e        - Teste end-to-end")
        print("  @pytest.mark.smoke      - Teste rápido/básico")
        print("  @pytest.mark.slow       - Teste demorado")
        print("  @pytest.mark.database   - Teste de banco")
        print("  @pytest.mark.auth       - Teste de autenticação")
        print()
        print("🔧 COMANDOS DIRETOS:")
        print("  pytest tests/unit/                    - Testes unitários")
        print("  pytest -m smoke                       - Testes rápidos")
        print("  pytest --cov=src tests/               - Com cobertura")
        print("  pytest --html=report.html tests/      - Com relatório")
        print()
        print("📚 DOCUMENTAÇÃO COMPLETA:")
        print("  Veja: docs/TESTES_ORGANIZADOS.md")
        print("="*60)
        return True
    
    def handle_choice(self, choice):
        """Processa escolha do usuário"""
        handlers = {
            '1': self.run_unit_tests,
            '2': self.run_integration_tests,
            '3': self.run_e2e_tests,
            '4': self.run_api_tests,
            '5': self.run_smoke_tests,
            '6': self.run_full_tests,
            '7': self.run_database_tests,
            '8': self.run_auth_tests,
            '9': self.run_specific_file,
            '10': self.run_with_coverage,
            '11': self.run_all_tests,
            '12': self.generate_html_report,
            '13': self.clean_cache,
            '14': self.check_configuration,
            '15': self.list_tests,
            '16': self.show_help,
        }
        
        handler = handlers.get(choice)
        if handler:
            return handler()
        else:
            print("❌ Opção inválida")
            return False
    
    def run(self):
        """Executa o menu interativo"""
        while True:
            self.show_menu()
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '0':
                print("\n👋 Saindo do sistema de testes...")
                break
            
            self.handle_choice(choice)
            
            if choice != '0':
                input("\nPressione Enter para continuar...")


def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Modo não-interativo
        runner = TestRunner()
        choice = sys.argv[1]
        runner.handle_choice(choice)
    else:
        # Modo interativo
        runner = TestRunner()
        runner.run()


if __name__ == "__main__":
    main() 