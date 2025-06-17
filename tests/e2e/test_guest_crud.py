"""
Testes CRUD automatizados para funcionalidades de hóspedes
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import time
from tests.pages.guest_pages import GuestRegistrationPage, GuestListPage, GuestEditPage
from tests.pages.admin_pages import AdminLoginPage
from tests.helpers.performance_helpers import (
    smart_wait_for_page_load, 
    smart_wait_for_url_change,
    turbo_wait_for_navigation,
    quick_sleep
)


# Content replacement for the entire TestGuestCRUD class
class TestGuestCRUD:
    """Classe de testes para operações CRUD de hóspedes"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_server):
        """Setup para cada teste"""
        try:
            self.driver = driver
            self.base_url = flask_server # http://localhost:5000
            self.guest_registration = GuestRegistrationPage(driver, base_url=self.base_url)
            self.guest_list = GuestListPage(driver, base_url=self.base_url)
            self.guest_edit = GuestEditPage(driver, base_url=self.base_url)
            self.admin_login_page = AdminLoginPage(driver, base_url=self.base_url)
        except Exception as e:
            pytest.fail(f"Falha no setup do teste: {e}")
    
    def test_create_guest_valid_data(self, sample_guest_data, test_database): # Added test_database
        """Teste: Criar hóspede com dados válidos"""
        try:
            # Arrange
            valid_data = sample_guest_data.copy()
            created_email = f"test.create.valid.{time.time()}@example.com"
            # More robust unique CPF: last 11 digits of timestamp in milliseconds
            created_cpf = str(int(time.time() * 1000))[-11:]
            valid_data["email"] = created_email
            valid_data["cpf"] = created_cpf

            # Act
            self.guest_registration.register_guest(valid_data)
            
            self.guest_registration.wait_for_url_contains(self.base_url + "/", timeout=10)
            assert self.base_url + "/" == self.driver.current_url, \
                f"Deveria redirecionar para a página inicial. URL atual: {self.driver.current_url}"

            # Verificar no DB
            conn = test_database
            cursor = conn.cursor()
            cursor.execute("SELECT email, cpf, ativo FROM hospedes WHERE email = ?", (created_email,))
            db_guest = cursor.fetchone()
            assert db_guest is not None, f"Hóspede {created_email} não encontrado no DB após cadastro."
            assert db_guest['cpf'] == created_cpf, "CPF no DB não confere."
            assert db_guest['ativo'] == 1, "Hóspede recém-criado deveria estar ativo."
            print(f"DB CHECK (create_valid): Guest {created_email} created and active.")

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_guest_create_valid_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste de criação de hóspede (válido) falhou: {e}")
    
    def test_create_guest_invalid_data(self, sample_guest_data):
        """Teste: Criar hóspede com dados inválidos"""
        try:
            invalid_data = sample_guest_data.copy()
            invalid_data['email'] = 'email_invalido_sem_arroba' # Invalid email
            
            self.guest_registration.register_guest(invalid_data)
            
            self.guest_registration.wait_for_url_contains("/hospede/cadastro", timeout=5)
            assert "/hospede/cadastro" in self.driver.current_url, \
                f"Deveria permanecer na página de cadastro. URL atual: {self.driver.current_url}"
            
            # Idealmente, verificaríamos uma mensagem de erro específica.
            # error_message = self.guest_registration.get_error_message()
            # assert "Email inválido" in error_message # Ou outra mensagem esperada

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_guest_create_invalid_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste de criação de hóspede (inválido) falhou: {e}")
    
    def test_read_guest_list(self, admin_credentials, sample_guest_data, test_database):
        """Teste: Listar hóspedes (funcionalidade administrativa)"""
        try:
            self.admin_login_page.navigate()
            self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
            self.admin_login_page.wait_for_url_contains("/admin/painel", timeout=10)
            
            guest_data_for_list_test = sample_guest_data.copy()
            created_guest_email = f"guest.list.test.{time.time()}@example.com"
            # More robust unique CPF: last 11 digits of timestamp in milliseconds
            created_guest_cpf = str(int(time.time() * 1000))[-11:]
            guest_data_for_list_test["email"] = created_guest_email
            guest_data_for_list_test["cpf"] = created_guest_cpf
            
            self.guest_registration.register_guest(guest_data_for_list_test)
            self.guest_registration.wait_for_url_contains(self.base_url + "/", timeout=10)
            print(f"Redirected to {self.driver.current_url} after public guest registration.")

            conn = test_database
            cursor = conn.cursor()
            cursor.execute("SELECT nome_completo, email, cpf, ativo FROM hospedes WHERE email = ?", (created_guest_email,))
            db_guest = cursor.fetchone()
            
            assert db_guest is not None, f"Hóspede {created_guest_email} não encontrado no DB."
            assert db_guest['email'] == created_guest_email
            assert db_guest['cpf'] == created_guest_cpf
            assert db_guest['ativo'] == 1, f"Hóspede {created_guest_email} no DB não está ativo (ativo={db_guest['ativo']})."
            print(f"DB CHECK (read_list): Guest {created_guest_email} (Nome: {db_guest['nome_completo']}, CPF: {db_guest['cpf']}) found, active.")

            self.guest_list.navigate()
            self.guest_list.wait_for_url_contains("/admin/hospedes", timeout=10)
            
            current_url = self.driver.current_url
            assert "/admin/hospedes" in current_url, f"Deveria estar em /admin/hospedes. URL: {current_url}"
            
            quick_sleep(1.5) # Increased sleep for table rendering, if very dynamic
            page_source = self.driver.page_source
            assert created_guest_email in page_source, \
                f"Email {created_guest_email} não encontrado em /admin/hospedes. Page source (1500 chars): {page_source[:1500]}"

            assert self.guest_list.is_element_present(self.guest_list.GUESTS_TABLE), \
                "Tabela de hóspedes (.table) não encontrada em /admin/hospedes."

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_read_guest_list_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste test_read_guest_list falhou: {e}")
    
    def test_search_guest(self, sample_guest_data, admin_credentials, test_database):
        """Teste: Buscar hóspede por nome e email"""
        try:
            self.admin_login_page.navigate()
            self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
            self.admin_login_page.wait_for_url_contains("/admin/painel", timeout=10)

            # Dados únicos para o hóspede a ser buscado
            timestamp_suffix = str(int(time.time()))
            search_guest_email = f"search.guest.{timestamp_suffix}@example.com"
            search_guest_nome = f"Buscavel Silva {timestamp_suffix}"
            # More robust unique CPF: last 11 digits of timestamp in milliseconds
            search_guest_cpf = str(int(time.time() * 1000))[-11:]

            guest_data = sample_guest_data.copy()
            guest_data["email"] = search_guest_email
            guest_data["nome_completo"] = search_guest_nome
            guest_data["cpf"] = search_guest_cpf
            
            self.guest_registration.register_guest(guest_data) # Cria o hóspede
            self.guest_registration.wait_for_url_contains(self.base_url + "/", timeout=10)
            
            self.guest_list.navigate() # Vai para a lista de admin
            self.guest_list.wait_for_url_contains("/admin/hospedes", timeout=10)
            
            # Buscar por nome completo
            print(f"Buscando por nome: {search_guest_nome}")
            self.guest_list.search_guest(search_guest_nome)
            quick_sleep(1.5) # Aguardar resultados da busca
            page_source_nome = self.driver.page_source
            assert search_guest_email in page_source_nome, f"Email {search_guest_email} não encontrado após busca por nome '{search_guest_nome}'."
            assert self.guest_list.get_guest_count() >= 1, "Contagem de hóspedes < 1 após busca por nome."

            # Limpar busca (recarregando a página) e buscar por email
            print(f"Buscando por email: {search_guest_email}")
            self.guest_list.navigate()
            self.guest_list.wait_for_url_contains("/admin/hospedes", timeout=10)
            self.guest_list.search_guest(search_guest_email)
            quick_sleep(1.5)
            page_source_email = self.driver.page_source
            assert search_guest_email in page_source_email, f"Email {search_guest_email} não encontrado após busca por email."
            assert self.guest_list.get_guest_count() >= 1, "Contagem de hóspedes < 1 após busca por email."

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_search_guest_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste test_search_guest falhou: {e}")

    def test_update_guest(self, sample_guest_data, admin_credentials, test_database):
        """Teste: Atualizar dados do hóspede"""
        try:
            self.admin_login_page.navigate()
            self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
            self.admin_login_page.wait_for_url_contains("/admin/painel", timeout=10)

            timestamp_suffix = str(int(time.time()))
            original_email = f"update.orig.{timestamp_suffix}@example.com"
            original_nome = f"Original Nome {timestamp_suffix}"
            # More robust unique CPF: last 11 digits of timestamp in milliseconds
            original_cpf = str(int(time.time() * 1000))[-11:]

            guest_data = sample_guest_data.copy()
            guest_data["email"] = original_email
            guest_data["nome_completo"] = original_nome
            guest_data["cpf"] = original_cpf

            self.guest_registration.register_guest(guest_data)
            self.guest_registration.wait_for_url_contains(self.base_url + "/", timeout=10)

            self.guest_list.navigate()
            self.guest_list.wait_for_url_contains("/admin/hospedes", timeout=10)
            quick_sleep(1)

            conn = test_database
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM hospedes WHERE email = ?", (original_email,))
            db_guest_for_edit = cursor.fetchone()
            assert db_guest_for_edit is not None, f"Hóspede {original_email} não encontrado no DB para obter ID."
            hospede_id_for_edit = db_guest_for_edit['id']

            rows = self.guest_list.find_elements(self.guest_list.GUEST_ROWS)
            guest_index_to_edit = -1
            for i, row in enumerate(rows):
                if original_email in row.text:
                    guest_index_to_edit = i
                    break
            
            assert guest_index_to_edit != -1, f"Hóspede {original_email} não encontrado na UI para edição."
            self.guest_list.click_edit_by_index(guest_index_to_edit)
            
            self.guest_edit.wait_for_url_contains(f"/admin/hospede/{hospede_id_for_edit}/editar", timeout=10)

            updated_nome = f"Nome Atualizado {timestamp_suffix}"
            updated_telefone = f"(99) 9{timestamp_suffix[-4:]}-{timestamp_suffix[-8:-4]}"
            
            update_payload = {"nome_completo": updated_nome, "telefone": updated_telefone}
            
            self.guest_edit.fill_form(update_payload)
            self.guest_edit.submit_form()
            
            self.guest_list.wait_for_url_contains("/admin/hospedes", timeout=10)
            quick_sleep(1.5)
            page_source_after_update = self.driver.page_source
            assert updated_nome in page_source_after_update, f"Nome '{updated_nome}' não encontrado após update."
            assert original_email in page_source_after_update, f"Email '{original_email}' deveria persistir."
            assert updated_telefone in page_source_after_update, f"Telefone '{updated_telefone}' não encontrado após update."

            # Verificar no DB
            cursor.execute("SELECT nome_completo, telefone FROM hospedes WHERE id = ?", (hospede_id_for_edit,))
            db_updated_guest = cursor.fetchone()
            assert db_updated_guest['nome_completo'] == updated_nome
            assert db_updated_guest['telefone'] == updated_telefone
            print(f"DB CHECK (update): Guest {original_email} updated successfully.")

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_update_guest_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste test_update_guest falhou: {e}")

    def test_delete_guest(self, sample_guest_data, admin_credentials, test_database):
        """Teste: Excluir hóspede (inativar)"""
        try:
            self.admin_login_page.navigate()
            self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
            self.admin_login_page.wait_for_url_contains("/admin/painel", timeout=10)

            timestamp_suffix = str(int(time.time()))
            guest_to_delete_email = f"delete.guest.{timestamp_suffix}@example.com"
            guest_to_delete_nome = f"Deletavel Silva {timestamp_suffix}"
            # More robust unique CPF: last 11 digits of timestamp in milliseconds
            guest_to_delete_cpf = str(int(time.time() * 1000))[-11:]

            guest_data = sample_guest_data.copy()
            guest_data["email"] = guest_to_delete_email
            guest_data["nome_completo"] = guest_to_delete_nome
            guest_data["cpf"] = guest_to_delete_cpf
            
            self.guest_registration.register_guest(guest_data)
            self.guest_registration.wait_for_url_contains(self.base_url + "/", timeout=10)

            self.guest_list.navigate()
            self.guest_list.wait_for_url_contains("/admin/hospedes", timeout=10)
            quick_sleep(1)

            assert guest_to_delete_email in self.driver.page_source, f"Hóspede {guest_to_delete_email} não listado antes da exclusão."

            rows = self.guest_list.find_elements(self.guest_list.GUEST_ROWS)
            guest_index_to_delete = -1
            for i, row in enumerate(rows):
                if guest_to_delete_email in row.text:
                    guest_index_to_delete = i
                    break
            
            assert guest_index_to_delete != -1, f"Hóspede {guest_to_delete_email} não encontrado na UI para exclusão."
            
            if hasattr(self.guest_list, 'click_delete_by_index'):
                 self.guest_list.click_delete_by_index(guest_index_to_delete)
                 # Assumindo que o PageObject lida com confirmação de modal se houver.
            else:
                pytest.skip("Método click_delete_by_index não implementado. Teste de exclusão pulado.")

            self.guest_list.wait_for_url_contains("/admin/hospedes", timeout=10)
            quick_sleep(1.5)

            conn = test_database
            cursor = conn.cursor()
            cursor.execute("SELECT ativo FROM hospedes WHERE email = ?", (guest_to_delete_email,))
            db_status = cursor.fetchone()
            assert db_status is not None, f"Hóspede {guest_to_delete_email} não encontrado no DB após suposta exclusão."
            assert db_status['ativo'] == 0, f"Hóspede {guest_to_delete_email} ainda está ativo no DB (ativo={db_status['ativo']})."
            print(f"DB CHECK (delete): Guest {guest_to_delete_email} is inactive in DB.")
            
            # A lista /admin/hospedes não filtra por 'ativo' por padrão, então o hóspede ainda estará lá.
            # Seria ideal verificar se o status "Inativo" é exibido na UI.
            page_source_after_delete = self.driver.page_source
            assert guest_to_delete_email in page_source_after_delete, \
                f"Hóspede {guest_to_delete_email} deveria estar na lista (como inativo), mas não foi."
            # Para uma verificação mais completa, precisaríamos de um método para ler o status da linha na tabela.

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_delete_guest_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste test_delete_guest falhou: {e}")

    def test_guest_form_validation(self):
        """Teste: Validação de formulário de hóspede (campos obrigatórios)"""
        try:
            self.guest_registration.navigate()
            self.guest_registration.submit_form()
            
            self.guest_registration.wait_for_url_contains("/hospede/cadastro", timeout=5)
            assert "/hospede/cadastro" in self.driver.current_url, "Submissão de formulário vazio deveria permanecer na página."
            
            # Verificar se uma mensagem de erro geral ou específica de campo obrigatório é mostrada.
            # error_message = self.guest_registration.get_error_message() # Supondo que este método exista
            # assert "obrigatório" in error_message.lower() or "preencha" in error_message.lower()
            # A rota processar_cadastro_hospede em app.py usa flash messages.
            # Precisaríamos verificar a presença de uma flash message de erro.
            # Ex: assert "Todos os campos são obrigatórios!" in self.driver.page_source

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_guest_form_validation_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste test_guest_form_validation falhou: {e}")

    def test_guest_navigation(self):
        """Teste: Navegação básica entre páginas relacionadas a hóspedes e admin"""
        try:
            # Navegar para cadastro de hóspede
            self.guest_registration.navigate()
            self.guest_registration.wait_for_url_contains("/hospede/cadastro", timeout=10)
            assert "/hospede/cadastro" in self.driver.current_url

            # Navegar para página inicial
            self.driver.get(self.base_url)
            self.guest_registration.wait_for_url_contains(self.base_url + "/", timeout=10)
            assert self.base_url + "/" == self.driver.current_url
            
            # Navegar para login de admin
            self.admin_login_page.navigate()
            self.admin_login_page.wait_for_url_contains("/admin/login", timeout=10)
            assert "/admin/login" in self.driver.current_url

        except Exception as e:
            try:
                screenshot_path = os.path.join(project_root, "tests", "screenshots", "test_guest_navigation_error.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
            except Exception as sc_e:
                print(f"Erro ao salvar screenshot: {sc_e}")
            pytest.fail(f"Teste test_guest_navigation falhou: {e}")
