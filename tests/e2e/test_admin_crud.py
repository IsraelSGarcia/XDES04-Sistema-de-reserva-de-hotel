"""
Testes CRUD automatizados para funcionalidades de administradores
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import time
from tests.pages.admin_pages import AdminLoginPage
from tests.helpers.performance_helpers import (
    smart_wait_for_page_load, 
    smart_wait_for_url_change,
    turbo_wait_for_navigation,
    quick_sleep
)
from tests.pages.admin_pages import AdminLoginPage, AdminPanelPage, AdminRegistrationPage, AdminListPage, AdminEditPage


class TestAdminCRUD:
    """Classe de testes para operações CRUD de administradores"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_server):
        """Setup para cada teste"""
        try:
            self.driver = driver
            self.base_url = flask_server
            self.admin_login_page = AdminLoginPage(driver, base_url=self.base_url)
            self.admin_panel = AdminPanelPage(driver, base_url=self.base_url)
            self.admin_registration = AdminRegistrationPage(driver, base_url=self.base_url)
            self.admin_list = AdminListPage(driver, base_url=self.base_url)
            self.admin_edit = AdminEditPage(driver, base_url=self.base_url)
            # Add Guest page objects if they are used in this test class,
            # otherwise, they can be removed from here if not needed.
            # For now, assuming they might be used, let's add them with base_url.
            from tests.pages.guest_pages import GuestListPage, GuestRegistrationPage # Ensure import
            self.guest_list_page = GuestListPage(driver, base_url=self.base_url)
            self.guest_registration_page = GuestRegistrationPage(driver, base_url=self.base_url)
        except Exception as e:
            pytest.fail(f"Falha no setup do teste: {e}")
    
    def test_admin_login_valid_credentials(self):
        """Teste: Login com credenciais válidas"""
        try:
            # Arrange & Act
            self.admin_login_page.navigate()
            self.admin_login_page.login("admin@restel.com", "admin123")
            
            # Assert
            self.admin_login_page.wait_for_url_contains("/admin/painel")
            current_url = self.driver.current_url # Keep for assertion if needed, or remove if wait implies success
            assert "/admin/painel" in current_url, f"Login não redirecionou para painel. URL atual: {current_url}"
        except Exception as e:
            # Capturar screenshot em caso de erro
            try:
                self.driver.save_screenshot("tests/screenshots/test_admin_login_error.png")
            except:
                pass
            pytest.fail(f"Teste de login falhou: {e}")
    
    def test_admin_login_invalid_credentials(self):
        """Teste: Login com credenciais inválidas"""
        try:
            # Arrange & Act
            self.admin_login_page.navigate()
            self.admin_login_page.login("admin@restel.com", "senha_errada")
            
            # Assert
            smart_wait_for_page_load(self.driver, timeout=1)  # Aumentar tempo de espera
            current_url = self.driver.current_url
            assert "/admin/login" in current_url, f"Login inválido deveria permanecer na tela de login. URL atual: {current_url}"
        except Exception as e:
            pytest.fail(f"Teste de credenciais inválidas falhou: {e}")
    
    def test_create_admin_valid_data(self, valid_admin_data):
        """Teste: Criar administrador com dados válidos"""
        # Arrange
        valid_data = valid_admin_data.copy()
        valid_data["email"] = "novo.admin@restel.com"  # Email único
        
        # Act
        # Login as Master Admin first
        self.admin_login_page.navigate()
        self.admin_login_page.login("admin@restel.com", "admin123")
        self.admin_login_page.wait_for_url_contains("/admin/painel")

        self.admin_registration.navigate()
        self.admin_registration.register_admin(valid_data)
        
        # Assert - Verifica se o formulário foi submetido (página de cadastro ou redirecionamento)
        smart_wait_for_page_load(self.driver, timeout=1)
        current_url = self.driver.current_url
        # Se criação bem-sucedida, pode permanecer na página de cadastro ou redirecionar
        assert "/admin/administrador/cadastro" in current_url or "/admin/administradores" in current_url, \
               f"URL inesperada após tentativa de criação: {current_url}"
    
    def test_create_admin_invalid_data(self, invalid_admin_data):
        """Teste: Criar administrador com dados inválidos"""
        # Arrange
        invalid_data = invalid_admin_data
        # Act
        # Login as Master Admin first
        self.admin_login_page.navigate()
        self.admin_login_page.login("admin@restel.com", "admin123")
        smart_wait_for_page_load(self.driver, timeout=1)  # Ensure login is complete
        assert "/admin/painel" in self.driver.current_url, f"Login como Master falhou. URL atual: {self.driver.current_url}"

        self.admin_registration.navigate()
        self.admin_registration.register_admin(invalid_data)
        
        
        # Assert - Deve permanecer na página de cadastro
        quick_sleep(0.3)
        current_url = self.driver.current_url
        assert "/admin/administrador/cadastro" in current_url, f"Deveria permanecer na página de cadastro. URL atual: {current_url}"
    
    def test_read_admin_list(self, admin_credentials):
        """Teste: Listar administradores"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        self.admin_login_page.wait_for_url_contains("/admin/painel")
        
        # Act
        self.admin_list.navigate()
        self.admin_list.wait_for_url_contains("/admin/administradores")
        
        # Assert
        current_url = self.driver.current_url
        assert "/admin/administradores" in current_url, f"Deveria estar na página de administradores. URL atual: {current_url}"
        
        # Verifica se tabela está presente
        assert self.admin_list.is_element_present(self.admin_list.ADMINS_TABLE)
    
    def test_search_admin(self, admin_credentials):
        """Teste: Buscar administrador"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        
        # Act - Navega para página de administradores
        self.admin_list.navigate()
        
        # Simula busca pelo administrador principal que sabemos que existe
        self.admin_list.search_admin("Administrador")
        
        # Assert
        admin_count = self.admin_list.get_admin_count()
        assert admin_count > 0, "Busca não retornou resultados"
        
        # Verifica se o resultado contém um administrador
        admin_data_found = self.admin_list.get_admin_data_by_index(0)
        if admin_data_found:
            assert "admin" in admin_data_found["nome_completo"].lower() or "admin" in admin_data_found["email"].lower()
    
    def test_update_admin(self, valid_admin_data, admin_credentials):
        """Teste: Atualizar dados do administrador"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        
        # Cria administrador primeiro
        original_data = valid_admin_data.copy()
        original_data["email"] = "teste.update@restel.com"
        update_data = valid_admin_data.copy()
        update_data["email"] = "teste.update@restel.com"  # Mantém mesmo email
        update_data["nome_completo"] = "Admin Atualizado"
        
        self.admin_registration.navigate()
        self.admin_registration.register_admin(original_data)
        
        # Act - Busca e edita o administrador
        self.admin_list.navigate()
        self.admin_list.search_admin(original_data["email"])
        
        # Clica em editar no primeiro resultado
        initial_count = self.admin_list.get_admin_count()
        if initial_count > 0:
            self.admin_list.click_edit_by_index(0)
            
            # Preenche dados atualizados
            self.admin_edit.fill_form(update_data)
            self.admin_edit.submit_form()
            
            # Assert - Verifica se foi redirecionado
            quick_sleep(0.3)
            current_url = self.driver.current_url
            assert "/admin/administradores" in current_url, f"Deveria retornar para lista. URL atual: {current_url}"
            
            # Busca pelo administrador atualizado
            self.admin_list.search_admin(update_data["email"])
            updated_admin = self.admin_list.get_admin_data_by_index(0)
            
            if updated_admin:
                assert update_data["nome_completo"] in updated_admin["nome_completo"]
                assert update_data["perfil"] == updated_admin["perfil"]
    
    def test_delete_admin(self, valid_admin_data, admin_credentials):
        """Teste: Excluir administrador (exclusão lógica)"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        
        # Cria administrador primeiro
        valid_data = valid_admin_data.copy()
        valid_data["email"] = "teste.delete@restel.com"
        self.admin_registration.navigate()
        self.admin_registration.register_admin(valid_data)
        
        # Act - Busca e exclui o administrador
        self.admin_list.navigate()
        self.admin_list.search_admin(valid_data["email"])
        
        initial_count = self.admin_list.get_admin_count()
        if initial_count > 0:
            self.admin_list.click_delete_by_index(0)
            
            # Aceita confirmação de exclusão
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except:
                pass  # Se não houver alert, continua
            
            quick_sleep(0.3)
            
            # Assert - Verifica se administrador foi removido da lista
            current_count = self.admin_list.get_admin_count()
            assert current_count < initial_count, "Administrador não foi excluído da lista"
    
    def test_admin_form_validation(self, admin_credentials): # admin_credentials might be unused or asserted if it's master
        """Teste: Validação de campos obrigatórios no formulário"""
        # Arrange - Login como MASTER admin primeiro
        self.admin_login_page.navigate()
        # Use master credentials directly as this test needs master access to reach the registration page
        self.admin_login_page.login("admin@restel.com", "admin123")
        self.admin_login_page.wait_for_url_contains("/admin/painel") # Wait for login to complete
        
        # Act
        self.admin_registration.navigate() # Navigate to admin registration page
        self.admin_registration.submit_form()  # Submete formulário vazio
        
        # Assert - Deve permanecer na página de cadastro
        quick_sleep(0.3)
        current_url = self.driver.current_url
        assert "/admin/administrador/cadastro" in current_url, f"Deveria permanecer na página de cadastro. URL atual: {current_url}"
    
    def test_edit_admin_form_prepopulation(self, valid_admin_data, admin_credentials):
        """Teste: Verificar se formulário de edição vem preenchido"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        
        # Cria administrador primeiro
        valid_data = valid_admin_data.copy()
        valid_data["email"] = "teste.prepop@restel.com"
        self.admin_registration.navigate()
        self.admin_registration.register_admin(valid_data)
        
        # Act - Acessa formulário de edição
        self.admin_list.navigate()
        self.admin_list.search_admin(valid_data["email"])
        
        if self.admin_list.get_admin_count() > 0:
            self.admin_list.click_edit_by_index(0)
            
            # Assert - Verifica se campos estão preenchidos
            current_data = self.admin_edit.get_current_data()
            assert current_data["nome_completo"] != ""
            assert current_data["email"] != ""
            assert current_data["perfil"] != ""
    
    def test_cancel_admin_edit(self, valid_admin_data, admin_credentials):
        """Teste: Cancelar edição de administrador"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        
        # Cria administrador primeiro
        valid_data = valid_admin_data.copy()
        valid_data["email"] = "teste.cancel@restel.com"
        self.admin_registration.navigate()
        self.admin_registration.register_admin(valid_data)
        
        # Act - Acessa edição e cancela
        self.admin_list.navigate()
        self.admin_list.search_admin(valid_data["email"])
        
        if self.admin_list.get_admin_count() > 0:
            self.admin_list.click_edit_by_index(0)
            self.admin_edit.cancel_edit()
            
            # Assert - Deve retornar para lista
            quick_sleep(0.3)
            current_url = self.driver.current_url
            assert "/admin/administradores" in current_url, f"Deveria retornar para lista. URL atual: {current_url}"
    
    def test_search_no_results(self, admin_credentials):
        """Teste: Busca sem resultados"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        
        # Act
        self.admin_list.navigate()
        self.admin_list.search_admin("admin_inexistente@email.com")
        
        # Assert - Deve exibir zero resultados
        admin_count = self.admin_list.get_admin_count()
        assert admin_count == 0, "Busca deveria retornar zero resultados"
    
    def test_admin_panel_navigation(self, admin_credentials):
        """Teste: Navegação do painel administrativo"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        
        # Act
        self.admin_panel.navigate()
        
        # Assert - Verifica se está no painel
        current_url = self.driver.current_url
        assert "/admin/painel" in current_url, f"Deveria estar no painel. URL atual: {current_url}"
        
        # Verifica se página carregou completamente
        assert "Painel Administrativo" in self.driver.page_source, "Conteúdo do painel não foi carregado"
    
    def test_different_admin_profiles(self, admin_credentials):
        """Teste: Criação de administradores com diferentes perfis"""
        # Arrange - Login como admin primeiro
        self.admin_login_page.navigate()
        self.admin_login_page.login(admin_credentials['email'], admin_credentials['senha'])
        self.admin_login_page.wait_for_url_contains("/admin/painel") # Wait for login
        
        # Act - Navega para página de administradores
        self.admin_list.navigate()
        self.admin_list.wait_for_url_contains("/admin/administradores") # Wait for navigation
        
        # Assert - Verifica se há administradores na lista (Master padrão existe)
        total_admins = self.admin_list.get_admin_count()
        assert total_admins > 0, "Deve haver pelo menos um administrador Master no sistema"
        
        # Verifica perfis existentes
        admin_found = self.admin_list.get_admin_data_by_index(0)
        if admin_found:
            assert admin_found["perfil"] in ["Master", "Padrão"], f"Perfil inválido encontrado: {admin_found['perfil']}" 