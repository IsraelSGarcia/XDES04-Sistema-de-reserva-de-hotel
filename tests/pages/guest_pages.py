"""
Page Objects para páginas de hóspedes
"""
from .base_page import BasePage
from selenium.webdriver.common.by import By


class GuestPages(BasePage):
    """Page Object para páginas de hóspedes"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "http://localhost:5000"
    
    # Locators
    NOME_FIELD = (By.ID, "nome_completo")
    EMAIL_FIELD = (By.ID, "email")
    CPF_FIELD = (By.ID, "cpf")
    TELEFONE_FIELD = (By.ID, "telefone")
    SENHA_FIELD = (By.ID, "senha")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    def go_to_cadastro(self):
        """Navega para página de cadastro"""
        self.go_to(f"{self.base_url}/cadastro")
    
    def fill_cadastro_form(self, guest_data):
        """Preenche formulário de cadastro"""
        self.send_keys(self.NOME_FIELD, guest_data['nome_completo'])
        self.send_keys(self.EMAIL_FIELD, guest_data['email'])
        self.send_keys(self.CPF_FIELD, guest_data['cpf'])
        self.send_keys(self.TELEFONE_FIELD, guest_data['telefone'])
        self.send_keys(self.SENHA_FIELD, guest_data['senha'])
    
    def submit_cadastro(self):
        """Submete formulário de cadastro"""
        self.click(self.SUBMIT_BUTTON)
    
    def cadastrar_hospede(self, guest_data):
        """Processo completo de cadastro"""
        self.go_to_cadastro()
        self.fill_cadastro_form(guest_data)
        self.submit_cadastro()


class GuestRegistrationPage(BasePage):
    """Page Object para registro de hóspedes"""
    
    # Locators
    NOME_FIELD = (By.ID, "nome_completo")
    EMAIL_FIELD = (By.ID, "email")
    TELEFONE_FIELD = (By.ID, "telefone")
    CPF_FIELD = (By.ID, "cpf")
    SENHA_FIELD = (By.ID, "senha")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "alert-success")
    ERROR_MESSAGE = (By.CLASS_NAME, "alert-danger")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/hospede/cadastro"
    
    def navigate(self):
        """Navega para página de registro de hóspede"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def fill_form(self, guest_data):
        """Preenche formulário de registro"""
        self.send_keys(self.NOME_FIELD, guest_data.get("nome_completo", ""))
        self.send_keys(self.EMAIL_FIELD, guest_data.get("email", ""))
        self.send_keys(self.TELEFONE_FIELD, guest_data.get("telefone", ""))
        self.send_keys(self.CPF_FIELD, guest_data.get("cpf", ""))
        self.send_keys(self.SENHA_FIELD, guest_data.get("senha", ""))
    
    def submit_form(self):
        """Submete o formulário"""
        self.click(self.SUBMIT_BUTTON)
    
    def register_guest(self, guest_data):
        """Processo completo de registro"""
        self.navigate()
        self.fill_form(guest_data)
        self.submit_form()
    
    def get_success_message(self):
        """Obtém mensagem de sucesso"""
        return self.get_text(self.SUCCESS_MESSAGE)
    
    def get_error_message(self):
        """Obtém mensagem de erro"""
        return self.get_text(self.ERROR_MESSAGE)


class GuestListPage(BasePage):
    """Page Object para listagem de hóspedes"""
    
    # Locators
    GUESTS_TABLE = (By.CSS_SELECTOR, ".table")  # Primeira tabela na página
    SEARCH_FIELD = (By.ID, "nome")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    GUEST_ROWS = (By.CSS_SELECTOR, ".table tbody tr")
    EDIT_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-primary")
    DELETE_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-danger")
    NO_RESULTS_MESSAGE = (By.XPATH, "//h5[contains(text(), 'Nenhum hóspede encontrado')]")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://localhost:5000/admin/hospedes"
    
    def navigate(self):
        """Navega para página de listagem de hóspedes"""
        self.go_to(self.url)
        self.wait_for_page_load()
    
    def search_guest(self, search_term):
        """Busca hóspede por termo"""
        self.send_keys(self.SEARCH_FIELD, search_term)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_page_load()
    
    def get_guest_count(self):
        """Retorna número de hóspedes na lista"""
        rows = self.find_elements(self.GUEST_ROWS)
        return len(rows)
    
    def get_guest_data_by_index(self, index):
        """Obtém dados do hóspede por índice na tabela"""
        rows = self.find_elements(self.GUEST_ROWS)
        if index < len(rows):
            cells = rows[index].find_elements(By.TAG_NAME, "td")
            if len(cells) >= 7:  # ID, Nome, Email, CPF, Telefone, Status, Data, Ações
                return {
                    "nome_completo": cells[1].text,  # Segunda coluna é o nome
                    "email": cells[2].text,          # Terceira coluna é o email
                    "telefone": cells[4].text,       # Quinta coluna é o telefone
                    "cpf": cells[3].text             # Quarta coluna é o CPF
                }
        return None
    
    def click_edit_by_index(self, index):
        """Clica no botão editar do hóspede por índice"""
        edit_buttons = self.find_elements(self.EDIT_BUTTONS)
        if index < len(edit_buttons):
            edit_buttons[index].click()
    
    def click_delete_by_index(self, index):
        """Clica no botão excluir do hóspede por índice"""
        delete_buttons = self.find_elements(self.DELETE_BUTTONS)
        if index < len(delete_buttons):
            delete_buttons[index].click()


class GuestEditPage(BasePage):
    """Page Object para edição de hóspedes"""
    
    # Locators
    NOME_FIELD = (By.ID, "nome_completo")
    EMAIL_FIELD = (By.ID, "email")
    TELEFONE_FIELD = (By.ID, "telefone")
    CPF_FIELD = (By.ID, "cpf")
    SENHA_FIELD = (By.ID, "senha")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".btn-secondary")
    
    def fill_form(self, guest_data):
        """Preenche formulário de edição"""
        self.send_keys(self.NOME_FIELD, guest_data.get("nome_completo", ""))
        self.send_keys(self.EMAIL_FIELD, guest_data.get("email", ""))
        self.send_keys(self.TELEFONE_FIELD, guest_data.get("telefone", ""))
        self.send_keys(self.CPF_FIELD, guest_data.get("cpf", ""))
        if guest_data.get("senha"):
            self.send_keys(self.SENHA_FIELD, guest_data["senha"])
    
    def submit_form(self):
        """Submete o formulário de edição"""
        self.click(self.SUBMIT_BUTTON)
    
    def cancel_edit(self):
        """Cancela a edição"""
        self.click(self.CANCEL_BUTTON)
    
    def get_current_data(self):
        """Obtém dados atuais do formulário"""
        return {
            "nome_completo": self.find_element(self.NOME_FIELD).get_attribute("value"),
            "email": self.find_element(self.EMAIL_FIELD).get_attribute("value"),
            "telefone": self.find_element(self.TELEFONE_FIELD).get_attribute("value"),
            "cpf": self.find_element(self.CPF_FIELD).get_attribute("value")
        } 