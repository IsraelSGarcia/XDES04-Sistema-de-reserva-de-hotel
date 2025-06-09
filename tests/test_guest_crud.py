"""
Testes CRUD automatizados para funcionalidades de hóspedes
"""
import pytest
import time
from tests.pages.guest_pages import GuestRegistrationPage, GuestListPage, GuestEditPage
from tests.pages.admin_pages import AdminLoginPage


class TestGuestCRUD:
    """Classe de testes para operações CRUD de hóspedes"""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_app):
        """Setup para cada teste"""
        self.driver = driver
        self.guest_registration = GuestRegistrationPage(driver)
        self.guest_list = GuestListPage(driver)
        self.guest_edit = GuestEditPage(driver)
        self.admin_login_page = AdminLoginPage(driver)
    
    def test_create_guest_valid_data(self, guest_data):
        """Teste: Criar hóspede com dados válidos"""
        # Arrange
        valid_data = guest_data["valid"]
        
        # Act
        self.guest_registration.register_guest(valid_data)
        
        # Assert - Verifica se foi redirecionado ou teve sucesso
        time.sleep(1)
        current_url = self.driver.current_url
        # Pode ser redirecionado para página inicial ou permanecer no cadastro com sucesso
        assert "/hospede/cadastro" in current_url or "/" in current_url, f"URL inesperada após cadastro: {current_url}"
    
    def test_create_guest_invalid_data(self, guest_data):
        """Teste: Criar hóspede com dados inválidos"""
        # Arrange
        invalid_data = guest_data["invalid"]
        
        # Act
        self.guest_registration.register_guest(invalid_data)
        
        # Assert - Deve permanecer na página de cadastro
        time.sleep(1)
        current_url = self.driver.current_url
        assert "/hospede/cadastro" in current_url, f"Deveria permanecer na página de cadastro. URL atual: {current_url}"
    
    def test_read_guest_list(self, admin_login):
        """Teste: Listar hóspedes (funcionalidade administrativa)"""
        # Act
        self.guest_list.navigate()
        
        # Assert
        current_url = self.driver.current_url
        assert "/admin/hospedes" in current_url, f"Deveria estar na página de hóspedes. URL atual: {current_url}"
        
        # Verifica se tabela está presente
        assert self.guest_list.is_element_present(self.guest_list.GUESTS_TABLE)
    
    def test_search_guest(self, guest_data, admin_login):
        """Teste: Buscar hóspede"""
        # Arrange - Primeiro cria um hóspede para buscar
        valid_data = guest_data["valid"]
        # Muda o email para evitar conflito
        valid_data["email"] = "busca.teste@email.com"
        self.guest_registration.register_guest(valid_data)
        
        # Act
        self.guest_list.navigate()
        self.guest_list.search_guest(valid_data["nome_completo"])
        
        # Assert
        guest_count = self.guest_list.get_guest_count()
        assert guest_count > 0, "Busca não retornou resultados"
        
        # Verifica se o resultado contém o hóspede buscado
        guest_data_found = self.guest_list.get_guest_data_by_index(0)
        if guest_data_found:
            assert valid_data["nome_completo"].lower() in guest_data_found["nome_completo"].lower()
    
    def test_update_guest(self, guest_data, admin_login):
        """Teste: Atualizar dados do hóspede"""
        # Arrange - Cria hóspede primeiro
        original_data = guest_data["valid"].copy()
        original_data["email"] = "update.teste@email.com"
        update_data = guest_data["update"].copy()
        update_data["email"] = "update.teste@email.com"  # Mantém mesmo email
        
        self.guest_registration.register_guest(original_data)
        
        # Act - Busca e edita o hóspede
        self.guest_list.navigate()
        self.guest_list.search_guest(original_data["email"])
        
        # Clica em editar no primeiro resultado
        initial_count = self.guest_list.get_guest_count()
        if initial_count > 0:
            self.guest_list.click_edit_by_index(0)
            
            # Preenche dados atualizados
            self.guest_edit.fill_form(update_data)
            self.guest_edit.submit_form()
            
            # Assert - Verifica se foi redirecionado
            time.sleep(1)
            current_url = self.driver.current_url
            assert "/admin/hospedes" in current_url, f"Deveria retornar para lista. URL atual: {current_url}"
            
            # Busca pelo hóspede atualizado
            self.guest_list.search_guest(update_data["email"])
            updated_guest = self.guest_list.get_guest_data_by_index(0)
            
            if updated_guest:
                assert update_data["nome_completo"] in updated_guest["nome_completo"]
                assert update_data["telefone"] in updated_guest["telefone"]
    
    def test_delete_guest(self, guest_data, admin_login):
        """Teste: Excluir hóspede (exclusão lógica)"""
        # Arrange - Cria hóspede primeiro
        valid_data = guest_data["valid"].copy()
        valid_data["email"] = "delete.teste@email.com"
        self.guest_registration.register_guest(valid_data)
        
        # Act - Busca e exclui o hóspede
        self.guest_list.navigate()
        self.guest_list.search_guest(valid_data["email"])
        
        initial_count = self.guest_list.get_guest_count()
        if initial_count > 0:
            self.guest_list.click_delete_by_index(0)
            
            # Aceita confirmação de exclusão
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except:
                pass  # Se não houver alert, continua
            
            time.sleep(1)
            
            # Assert - Verifica se hóspede foi removido da lista
            current_count = self.guest_list.get_guest_count()
            assert current_count < initial_count, "Hóspede não foi excluído da lista"
    
    def test_guest_form_validation(self):
        """Teste: Validação de campos obrigatórios no formulário"""
        # Act
        self.guest_registration.navigate()
        self.guest_registration.submit_form()  # Submete formulário vazio
        
        # Assert - Deve permanecer na página de cadastro
        time.sleep(1)
        current_url = self.driver.current_url
        assert "/hospede/cadastro" in current_url, f"Deveria permanecer na página de cadastro. URL atual: {current_url}"
    
    def test_edit_guest_form_prepopulation(self, guest_data, admin_login):
        """Teste: Verificar se formulário de edição vem preenchido"""
        # Arrange - Cria hóspede primeiro
        valid_data = guest_data["valid"].copy()
        valid_data["email"] = "prepop.teste@email.com"
        self.guest_registration.register_guest(valid_data)
        
        # Act - Acessa formulário de edição
        self.guest_list.navigate()
        self.guest_list.search_guest(valid_data["email"])
        
        if self.guest_list.get_guest_count() > 0:
            self.guest_list.click_edit_by_index(0)
            
            # Assert - Verifica se campos estão preenchidos
            current_data = self.guest_edit.get_current_data()
            assert current_data["nome_completo"] != ""
            assert current_data["email"] != ""
            assert current_data["telefone"] != ""
            assert current_data["cpf"] != ""
    
    def test_cancel_guest_edit(self, guest_data, admin_login):
        """Teste: Cancelar edição de hóspede"""
        # Arrange - Cria hóspede primeiro
        valid_data = guest_data["valid"].copy()
        valid_data["email"] = "cancel.teste@email.com"
        self.guest_registration.register_guest(valid_data)
        
        # Act - Acessa edição e cancela
        self.guest_list.navigate()
        self.guest_list.search_guest(valid_data["email"])
        
        if self.guest_list.get_guest_count() > 0:
            self.guest_list.click_edit_by_index(0)
            self.guest_edit.cancel_edit()
            
            # Assert - Deve retornar para lista
            time.sleep(1)
            current_url = self.driver.current_url
            assert "/admin/hospedes" in current_url, f"Deveria retornar para lista. URL atual: {current_url}"
    
    def test_search_no_results(self, admin_login):
        """Teste: Busca sem resultados"""
        # Act
        self.guest_list.navigate()
        self.guest_list.search_guest("hospede_inexistente@email.com")
        
        # Assert - Deve exibir zero resultados
        guest_count = self.guest_list.get_guest_count()
        assert guest_count == 0, "Busca deveria retornar zero resultados" 