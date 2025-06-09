"""
Utilitários e helpers para facilitar os testes automatizados
"""
import time
import random
import string
from datetime import datetime


class DataGenerator:
    """Gerador de dados de teste"""
    
    @staticmethod
    def generate_email(prefix="test"):
        """Gera email único para testes"""
        timestamp = int(time.time())
        return f"{prefix}_{timestamp}@restel.com"
    
    @staticmethod
    def generate_cpf():
        """Gera CPF formatado para testes (não necessariamente válido)"""
        numbers = [random.randint(0, 9) for _ in range(11)]
        return f"{numbers[0]}{numbers[1]}{numbers[2]}.{numbers[3]}{numbers[4]}{numbers[5]}.{numbers[6]}{numbers[7]}{numbers[8]}-{numbers[9]}{numbers[10]}"
    
    @staticmethod
    def generate_phone():
        """Gera telefone formatado para testes"""
        return f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    
    @staticmethod
    def generate_random_string(length=8):
        """Gera string aleatória"""
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    @staticmethod
    def generate_guest_data():
        """Gera dados completos de hóspede para testes"""
        name = DataGenerator.generate_random_string()
        return {
            "nome_completo": f"Hóspede {name}",
            "email": DataGenerator.generate_email("hospede"),
            "telefone": DataGenerator.generate_phone(),
            "cpf": DataGenerator.generate_cpf(),
            "senha": "senha123456"
        }
    
    @staticmethod
    def generate_admin_data(perfil="Padrão"):
        """Gera dados completos de administrador para testes"""
        name = DataGenerator.generate_random_string()
        return {
            "nome_completo": f"Admin {name}",
            "email": DataGenerator.generate_email("admin"),
            "senha": "senha123456",
            "perfil": perfil
        }


class TestAssertion:
    """Helpers para assertions nos testes"""
    
    @staticmethod
    def assert_url_contains(driver, expected_url_part, timeout=5):
        """Verifica se URL contém determinado texto com timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if expected_url_part in driver.current_url:
                return True
            time.sleep(0.5)
        
        current_url = driver.current_url
        raise AssertionError(f"URL '{current_url}' não contém '{expected_url_part}' após {timeout}s")
    
    @staticmethod
    def assert_element_text_contains(element, expected_text):
        """Verifica se texto do elemento contém o esperado"""
        actual_text = element.text.lower()
        expected_text = expected_text.lower()
        assert expected_text in actual_text, f"Texto '{actual_text}' não contém '{expected_text}'"
    
    @staticmethod
    def assert_form_fields_filled(page_object, fields):
        """Verifica se campos do formulário estão preenchidos"""
        for field_name in fields:
            field_value = getattr(page_object, f"get_{field_name}_value", lambda: "")()
            assert field_value != "", f"Campo '{field_name}' está vazio"


class ReportGenerator:
    """Helper para relatórios de teste (renomeado para evitar conflito com pytest)"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
    
    def start_test_run(self):
        """Inicia cronômetro para execução dos testes"""
        self.start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"INICIANDO TESTES AUTOMATIZADOS DO RESTEL")
        print(f"Data/Hora: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")
    
    def add_test_result(self, test_name, status, duration, details=""):
        """Adiciona resultado de teste"""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "duration": duration,
            "details": details
        })
    
    def generate_summary(self):
        """Gera sumário dos testes"""
        if not self.start_time:
            return
        
        end_time = datetime.now()
        total_duration = end_time - self.start_time
        
        passed = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed = len([r for r in self.test_results if r["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"\n{'='*60}")
        print(f"SUMÁRIO DOS TESTES")
        print(f"{'='*60}")
        print(f"Total de testes: {total}")
        print(f"Aprovados: {passed}")
        print(f"Falharam: {failed}")
        print(f"Taxa de sucesso: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print(f"Duração total: {total_duration}")
        print(f"{'='*60}")
        
        if failed > 0:
            print(f"\nTESTES QUE FALHARAM:")
            print(f"{'-'*40}")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"❌ {result['test']}")
                    if result["details"]:
                        print(f"   Detalhes: {result['details']}")


class DatabaseCleaner:
    """Helper para limpeza de dados de teste no banco"""
    
    @staticmethod
    def clean_test_data(driver, admin_login_page):
        """Remove dados de teste criados durante os testes"""
        try:
            # Faz login como admin
            admin_login_page.login("admin@restel.com", "admin123")
            
            # Aqui poderia implementar lógica para remover dados de teste
            # Por exemplo, excluir todos os registros que contêm "test" no email
            print("🧹 Limpeza de dados de teste concluída")
            
        except Exception as e:
            print(f"⚠️ Erro na limpeza de dados: {e}")


class ScreenshotHelper:
    """Helper para captura de screenshots em falhas"""
    
    @staticmethod
    def capture_failure_screenshot(driver, test_name):
        """Captura screenshot quando teste falha"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests/screenshots/failure_{test_name}_{timestamp}.png"
            driver.save_screenshot(filename)
            print(f"📸 Screenshot salvo: {filename}")
            return filename
        except Exception as e:
            print(f"⚠️ Erro ao capturar screenshot: {e}")
            return None


# Constantes úteis para testes
TEST_URLS = {
    "BASE": "http://localhost:5000",
    "LOGIN": "http://localhost:5000/admin/login",
    "PANEL": "http://localhost:5000/admin/painel",
    "GUESTS": "http://localhost:5000/admin/hospedes",
    "ADMINS": "http://localhost:5000/admin/administradores",
    "GUEST_REGISTER": "http://localhost:5000/hospede/cadastro",
    "ADMIN_REGISTER": "http://localhost:5000/admin/administrador/cadastro"
}

DEFAULT_TIMEOUTS = {
    "SHORT": 3,
    "MEDIUM": 10,
    "LONG": 30
} 