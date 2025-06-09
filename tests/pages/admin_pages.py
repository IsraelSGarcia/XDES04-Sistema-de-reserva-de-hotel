"""
Page Objects para funcionalidades de administradores
"""
import time
from selenium.webdriver.common.by import By
from .base_page import BasePage


class AdminLoginPage(BasePage):
    """Page Object para login de administradores"""
    
    # Locators
    EMAIL_FIELD = (By.ID, "email")
    PASSWORD_FIELD = (By.ID, "senha")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "alert-danger")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/admin/login"
    
    def navigate(self):
        """Navega para página de login"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def login(self, email, password):
        """Realiza login"""
        self.navigate()
        self.send_keys(self.EMAIL_FIELD, email)
        self.send_keys(self.PASSWORD_FIELD, password)
        self.submit_form()
    
    def submit_form(self):
        """Submete o formulário de login"""
        self.click(self.SUBMIT_BUTTON)
    
    def get_error_message(self):
        """Obtém mensagem de erro"""
        return self.get_text(self.ERROR_MESSAGE)


class AdminPanelPage(BasePage):
    """Page Object para painel administrativo"""
    
    # Locators
    GUESTS_CARD = (By.XPATH, "//a[contains(@href, 'gerenciar_hospedes')]")
    ADMINS_CARD = (By.XPATH, "//a[contains(@href, 'gerenciar_administradores')]")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "a[href='/admin/logout']")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/admin/painel"
    
    def navigate(self):
        """Navega para painel administrativo"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def go_to_guests(self):
        """Acessa gestão de hóspedes"""
        self.click(self.GUESTS_CARD)
    
    def go_to_admins(self):
        """Acessa gestão de administradores"""
        self.click(self.ADMINS_CARD)
    
    def logout(self):
        """Realiza logout"""
        self.click(self.LOGOUT_BUTTON)


class AdminRegistrationPage(BasePage):
    """Page Object para registro de administradores"""
    
    # Locators
    NOME_FIELD = (By.ID, "nome_completo")
    EMAIL_FIELD = (By.ID, "email")
    SENHA_FIELD = (By.ID, "senha")
    PERFIL_FIELD = (By.ID, "perfil")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "alert-success")
    ERROR_MESSAGE = (By.CLASS_NAME, "alert-danger")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/admin/administrador/cadastro"
    
    def navigate(self):
        """Navega para página de registro de administrador"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def fill_form(self, admin_data):
        """Preenche formulário de registro"""
        self.send_keys(self.NOME_FIELD, admin_data.get("nome_completo", ""))
        self.send_keys(self.EMAIL_FIELD, admin_data.get("email", ""))
        self.send_keys(self.SENHA_FIELD, admin_data.get("senha", ""))
        if admin_data.get("perfil"):
            self.select_dropdown(self.PERFIL_FIELD, admin_data["perfil"])
    
    def submit_form(self):
        """Submete o formulário"""
        self.click(self.SUBMIT_BUTTON)
    
    def register_admin(self, admin_data):
        """Processo completo de registro"""
        self.navigate()
        self.fill_form(admin_data)
        self.submit_form()
    
    def get_success_message(self):
        """Obtém mensagem de sucesso"""
        return self.get_text(self.SUCCESS_MESSAGE)
    
    def get_error_message(self):
        """Obtém mensagem de erro"""
        return self.get_text(self.ERROR_MESSAGE)


class AdminListPage(BasePage):
    """Page Object para listagem de administradores"""
    
    # Locators
    ADMINS_TABLE = (By.CSS_SELECTOR, ".table")  # Primeira tabela na página
    SEARCH_FIELD = (By.ID, "nome")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ADMIN_ROWS = (By.CSS_SELECTOR, ".table tbody tr")
    EDIT_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-primary")
    DELETE_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-danger")
    NO_RESULTS_MESSAGE = (By.XPATH, "//h5[contains(text(), 'Nenhum administrador encontrado')]")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/admin/administradores"
    
    def navigate(self):
        """Navega para página de listagem de administradores"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def search_admin(self, search_term):
        """Busca administrador por termo (simulado por busca na tabela)"""
        # A página de administradores não tem campo de busca
        # Simula busca armazenando o termo para filtrar depois
        self._search_term = search_term.lower()
        time.sleep(1)  # Pequena pausa para simular busca
    
    def get_admin_count(self):
        """Retorna número de administradores na lista"""
        rows = self.find_elements(self.ADMIN_ROWS)
        
        # Se há termo de busca, filtra por ele
        if hasattr(self, '_search_term') and self._search_term:
            filtered_rows = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:  # Tem pelo menos nome e email
                    nome = cells[1].text.lower()  # Segunda coluna é o nome
                    email = cells[2].text.lower()  # Terceira coluna é o email
                    if self._search_term in nome or self._search_term in email:
                        filtered_rows.append(row)
            return len(filtered_rows)
        
        return len(rows)
    
    def get_admin_data_by_index(self, index):
        """Obtém dados do administrador por índice na tabela"""
        rows = self.find_elements(self.ADMIN_ROWS)
        
        # Se há termo de busca, filtra os resultados primeiro
        if hasattr(self, '_search_term') and self._search_term:
            filtered_rows = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:  # Tem pelo menos nome e email
                    nome = cells[1].text.lower()  # Segunda coluna é o nome
                    email = cells[2].text.lower()  # Terceira coluna é o email
                    if self._search_term in nome or self._search_term in email:
                        filtered_rows.append(row)
            rows = filtered_rows
        
        if index < len(rows):
            cells = rows[index].find_elements(By.TAG_NAME, "td")
            if len(cells) >= 6:  # ID, Nome, Email, Perfil, Status, Data, Ações
                return {
                    "nome_completo": cells[1].text,  # Segunda coluna é o nome
                    "email": cells[2].text,          # Terceira coluna é o email
                    "perfil": cells[3].text          # Quarta coluna é o perfil
                }
        return None
    
    def click_edit_by_index(self, index):
        """Clica no botão editar do administrador por índice"""
        edit_buttons = self.find_elements(self.EDIT_BUTTONS)
        if index < len(edit_buttons):
            edit_buttons[index].click()
    
    def click_delete_by_index(self, index):
        """Clica no botão excluir do administrador por índice"""
        delete_buttons = self.find_elements(self.DELETE_BUTTONS)
        if index < len(delete_buttons):
            delete_buttons[index].click()


class AdminEditPage(BasePage):
    """Page Object para edição de administradores"""
    
    # Locators
    NOME_FIELD = (By.ID, "nome_completo")
    EMAIL_FIELD = (By.ID, "email")
    SENHA_FIELD = (By.ID, "senha")
    PERFIL_FIELD = (By.ID, "perfil")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".btn-secondary")
    
    def fill_form(self, admin_data):
        """Preenche formulário de edição"""
        self.send_keys(self.NOME_FIELD, admin_data.get("nome_completo", ""))
        self.send_keys(self.EMAIL_FIELD, admin_data.get("email", ""))
        if admin_data.get("senha"):
            self.send_keys(self.SENHA_FIELD, admin_data["senha"])
        if admin_data.get("perfil"):
            self.select_dropdown(self.PERFIL_FIELD, admin_data["perfil"])
    
    def submit_form(self):
        """Submete o formulário de edição"""
        self.click(self.SUBMIT_BUTTON)
    
    def cancel_edit(self):
        """Cancela a edição"""
        self.click(self.CANCEL_BUTTON)
    
    def get_current_data(self):
        """Obtém dados atuais do formulário"""
        perfil_element = self.find_element(self.PERFIL_FIELD)
        selected_option = perfil_element.find_element(By.CSS_SELECTOR, "option:checked")
        
        return {
            "nome_completo": self.find_element(self.NOME_FIELD).get_attribute("value"),
            "email": self.find_element(self.EMAIL_FIELD).get_attribute("value"),
            "perfil": selected_option.get_attribute("value")
        } 