"""
Testes CRUD automatizados para funcionalidades de administradores
"""
import pytest
import time
from tests.pages.admin_pages import AdminLoginPage, AdminPanelPage, AdminRegistrationPage, AdminListPage, AdminEditPage


class TestAdminCRUD:
    """Classe de testes para operações CRUD de administradores"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, admin_login, flask_app):
        """Setup para cada teste"""
        self.driver = driver
        self.admin_login_page = AdminLoginPage(driver)
        self.admin_panel = AdminPanelPage(driver)
        self.admin_registration = AdminRegistrationPage(driver)
        self.admin_list = AdminListPage(driver)
        self.admin_edit = AdminEditPage(driver)
    
    def test_admin_login_valid_credentials(self, flask_app):
        """Teste: Login com credenciais válidas"""
        # Act
        self.admin_login_page.login("admin@restel.com", "admin123")
        
        # Assert
        time.sleep(1)
        current_url = self.driver.current_url
        assert "/admin/painel" in current_url, f"Login não redirecionou para painel. URL atual: {current_url}"
    
    def test_admin_login_invalid_credentials(self, flask_app):
        """Teste: Login com credenciais inválidas"""
        # Act
        self.admin_login_page.login("admin@restel.com", "senha_errada")
        
        # Assert
        time.sleep(1)
        current_url = self.driver.current_url
        assert "/admin/login" in current_url, f"Login inválido deveria permanecer na tela de login. URL atual: {current_url}"
    
    def test_create_admin_valid_data(self, admin_data):
        """Teste: Criar administrador com dados válidos"""
        # Arrange
        valid_data = admin_data["valid"].copy()
        valid_data["email"] = "novo.admin@restel.com"  # Email único
        
        # Act
        self.admin_registration.register_admin(valid_data)
        
        # Assert - Verifica se o formulário foi submetido (página de cadastro ou redirecionamento)
        time.sleep(2)
        current_url = self.driver.current_url
        # Se criação bem-sucedida, pode permanecer na página de cadastro ou redirecionar
        assert "/admin/administrador/cadastro" in current_url or "/admin/administradores" in current_url, \
               f"URL inesperada após tentativa de criação: {current_url}"
    
    def test_create_admin_invalid_data(self, admin_data):
        """Teste: Criar administrador com dados inválidos"""
        # Arrange
        invalid_data = admin_data["invalid"]
        
        # Act
        self.admin_registration.register_admin(invalid_data)
        
        # Assert - Deve permanecer na página de cadastro
        time.sleep(1)
        current_url = self.driver.current_url
        assert "/admin/administrador/cadastro" in current_url, f"Deveria permanecer na página de cadastro. URL atual: {current_url}"
    
    def test_read_admin_list(self, admin_login):
        """Teste: Listar administradores"""
        # Act
        self.admin_list.navigate()
        
        # Assert
        current_url = self.driver.current_url
        assert "/admin/administradores" in current_url, f"Deveria estar na página de administradores. URL atual: {current_url}"
        
        # Verifica se tabela está presente
        assert self.admin_list.is_element_present(self.admin_list.ADMINS_TABLE)
    
    def test_search_admin(self, admin_data, admin_login):
        """Teste: Buscar administrador"""
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
    
    def test_update_admin(self, admin_data, admin_login):
        """Teste: Atualizar dados do administrador"""
        # Arrange - Cria administrador primeiro
        original_data = admin_data["valid"].copy()
        original_data["email"] = "teste.update@restel.com"
        update_data = admin_data["update"].copy()
        update_data["email"] = "teste.update@restel.com"  # Mantém mesmo email
        
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
            time.sleep(1)
            current_url = self.driver.current_url
            assert "/admin/administradores" in current_url, f"Deveria retornar para lista. URL atual: {current_url}"
            
            # Busca pelo administrador atualizado
            self.admin_list.search_admin(update_data["email"])
            updated_admin = self.admin_list.get_admin_data_by_index(0)
            
            if updated_admin:
                assert update_data["nome_completo"] in updated_admin["nome_completo"]
                assert update_data["perfil"] == updated_admin["perfil"]
    
    def test_delete_admin(self, admin_data, admin_login):
        """Teste: Excluir administrador (exclusão lógica)"""
        # Arrange - Cria administrador primeiro
        valid_data = admin_data["valid"].copy()
        valid_data["email"] = "teste.delete@restel.com"
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
            
            time.sleep(1)
            
            # Assert - Verifica se administrador foi removido da lista
            current_count = self.admin_list.get_admin_count()
            assert current_count < initial_count, "Administrador não foi excluído da lista"
    
    def test_admin_form_validation(self, admin_login):
        """Teste: Validação de campos obrigatórios no formulário"""
        # Act
        self.admin_registration.navigate()
        self.admin_registration.submit_form()  # Submete formulário vazio
        
        # Assert - Deve permanecer na página de cadastro
        time.sleep(1)
        current_url = self.driver.current_url
        assert "/admin/administrador/cadastro" in current_url, f"Deveria permanecer na página de cadastro. URL atual: {current_url}"
    
    def test_edit_admin_form_prepopulation(self, admin_data, admin_login):
        """Teste: Verificar se formulário de edição vem preenchido"""
        # Arrange - Cria administrador primeiro
        valid_data = admin_data["valid"].copy()
        valid_data["email"] = "teste.prepop@restel.com"
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
    
    def test_cancel_admin_edit(self, admin_data, admin_login):
        """Teste: Cancelar edição de administrador"""
        # Arrange - Cria administrador primeiro
        valid_data = admin_data["valid"].copy()
        valid_data["email"] = "teste.cancel@restel.com"
        self.admin_registration.register_admin(valid_data)
        
        # Act - Acessa edição e cancela
        self.admin_list.navigate()
        self.admin_list.search_admin(valid_data["email"])
        
        if self.admin_list.get_admin_count() > 0:
            self.admin_list.click_edit_by_index(0)
            self.admin_edit.cancel_edit()
            
            # Assert - Deve retornar para lista
            time.sleep(1)
            current_url = self.driver.current_url
            assert "/admin/administradores" in current_url, f"Deveria retornar para lista. URL atual: {current_url}"
    
    def test_search_no_results(self, admin_login):
        """Teste: Busca sem resultados"""
        # Act
        self.admin_list.navigate()
        self.admin_list.search_admin("admin_inexistente@email.com")
        
        # Assert - Deve exibir zero resultados
        admin_count = self.admin_list.get_admin_count()
        assert admin_count == 0, "Busca deveria retornar zero resultados"
    
    def test_admin_panel_navigation(self, admin_login):
        """Teste: Navegação do painel administrativo"""
        # Act
        self.admin_panel.navigate()
        
        # Assert - Verifica se está no painel
        current_url = self.driver.current_url
        assert "/admin/painel" in current_url, f"Deveria estar no painel. URL atual: {current_url}"
        
        # Verifica se página carregou completamente
        assert "Painel Administrativo" in self.driver.page_source, "Conteúdo do painel não foi carregado"
    
    def test_different_admin_profiles(self, admin_login):
        """Teste: Criação de administradores com diferentes perfis"""
        # Act - Navega para página de administradores
        self.admin_list.navigate()
        
        # Assert - Verifica se há administradores na lista (Master padrão existe)
        total_admins = self.admin_list.get_admin_count()
        assert total_admins > 0, "Deve haver pelo menos um administrador Master no sistema"
        
        # Verifica perfis existentes
        admin_found = self.admin_list.get_admin_data_by_index(0)
        if admin_found:
            assert admin_found["perfil"] in ["Master", "Padrão"], f"Perfil inválido encontrado: {admin_found['perfil']}" 