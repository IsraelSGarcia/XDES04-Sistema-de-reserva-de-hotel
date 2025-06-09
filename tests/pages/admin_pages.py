"""
Page Objects para funcionalidades de administradores
"""
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
        self.url = "http://localhost:5000/admin_login"
    
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
    GUESTS_CARD = (By.CSS_SELECTOR, "a[href='/admin_hospedes']")
    ADMINS_CARD = (By.CSS_SELECTOR, "a[href='/admin_administradores']")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "a[href='/logout']")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/admin_painel"
    
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
    NOME_FIELD = (By.ID, "nome")
    EMAIL_FIELD = (By.ID, "email")
    SENHA_FIELD = (By.ID, "senha")
    PERFIL_FIELD = (By.ID, "perfil")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "alert-success")
    ERROR_MESSAGE = (By.CLASS_NAME, "alert-danger")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/cadastro_admin"
    
    def navigate(self):
        """Navega para página de registro de administrador"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def fill_form(self, admin_data):
        """Preenche formulário de registro"""
        self.send_keys(self.NOME_FIELD, admin_data.get("nome", ""))
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
    ADMINS_TABLE = (By.ID, "tabelaAdministradores")
    SEARCH_FIELD = (By.ID, "busca")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[onclick='buscarAdministradores()']")
    ADMIN_ROWS = (By.CSS_SELECTOR, "#tabelaAdministradores tbody tr")
    EDIT_BUTTONS = (By.CSS_SELECTOR, ".btn-warning")
    DELETE_BUTTONS = (By.CSS_SELECTOR, ".btn-danger")
    NO_RESULTS_MESSAGE = (By.ID, "semResultados")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/admin_administradores"
    
    def navigate(self):
        """Navega para página de listagem de administradores"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def search_admin(self, search_term):
        """Busca administrador por termo"""
        self.send_keys(self.SEARCH_FIELD, search_term)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_page_load()
    
    def get_admin_count(self):
        """Retorna número de administradores na lista"""
        rows = self.find_elements(self.ADMIN_ROWS)
        # Filtra apenas linhas com dados (não mensagens de "sem resultados")
        return len([row for row in rows if row.find_elements(By.TAG_NAME, "td")])
    
    def get_admin_data_by_index(self, index):
        """Obtém dados do administrador por índice na tabela"""
        rows = self.find_elements(self.ADMIN_ROWS)
        if index < len(rows):
            cells = rows[index].find_elements(By.TAG_NAME, "td")
            if len(cells) >= 4:
                return {
                    "nome": cells[0].text,
                    "email": cells[1].text,
                    "perfil": cells[2].text
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
    NOME_FIELD = (By.ID, "nome")
    EMAIL_FIELD = (By.ID, "email")
    SENHA_FIELD = (By.ID, "senha")
    PERFIL_FIELD = (By.ID, "perfil")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".btn-secondary")
    
    def fill_form(self, admin_data):
        """Preenche formulário de edição"""
        self.send_keys(self.NOME_FIELD, admin_data.get("nome", ""))
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
            "nome": self.find_element(self.NOME_FIELD).get_attribute("value"),
            "email": self.find_element(self.EMAIL_FIELD).get_attribute("value"),
            "perfil": selected_option.get_attribute("value")
        } 