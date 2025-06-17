"""
Page Objects para funcionalidades de quartos
"""
import time
from selenium.webdriver.common.by import By
from .base_page import BasePage


class RoomListPage(BasePage):
    """Page Object para listagem de quartos"""
    
    # Locators
    ROOMS_TABLE = (By.CSS_SELECTOR, ".table")
    SEARCH_NUMBER_FIELD = (By.ID, "numero")
    SEARCH_TYPE_FIELD = (By.ID, "tipo")
    SEARCH_STATUS_FIELD = (By.ID, "status")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ROOM_ROWS = (By.CSS_SELECTOR, ".table tbody tr")
    EDIT_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-primary")
    DELETE_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-danger")
    ADD_ROOM_BUTTON = (By.XPATH, "//a[contains(@href, 'cadastro_quarto')]")
    NO_RESULTS_MESSAGE = (By.XPATH, "//h5[contains(text(), 'Nenhum quarto encontrado')]")
    
    def __init__(self, driver, base_url="http://localhost:5000"):
        super().__init__(driver)
        self.base_url = base_url
        self.list_url = f"{self.base_url}/admin/quartos"
    
    def navigate(self):
        """Navega para página de listagem de quartos"""
        self.go_to(self.list_url)
        self.wait_for_page_load()
    
    def search_room(self, number=None, room_type=None, status=None):
        """Busca quartos por filtros"""
        if number:
            self.send_keys(self.SEARCH_NUMBER_FIELD, number)
        if room_type:
            self.send_keys(self.SEARCH_TYPE_FIELD, room_type)
        if status:
            self.select_dropdown(self.SEARCH_STATUS_FIELD, status)
        
        self.click(self.SEARCH_BUTTON)
        time.sleep(1)  # Aguardar carregamento da busca
    
    def get_room_count(self):
        """Retorna número de quartos na lista"""
        return len(self.find_elements(self.ROOM_ROWS))
    
    def get_room_data_by_index(self, index):
        """Obtém dados do quarto por índice na tabela"""
        rows = self.find_elements(self.ROOM_ROWS)
        if index < len(rows):
            cells = rows[index].find_elements(By.TAG_NAME, "td")
            if len(cells) >= 6:  # Número, Tipo, Capacidade, Preço, Status, Data, Ações
                return {
                    "numero": cells[0].text,
                    "tipo": cells[1].text,
                    "capacidade": cells[2].text.replace("👥 ", ""),
                    "preco_diaria": cells[3].text.replace("R$ ", ""),
                    "status": cells[4].text
                }
        return None
    
    def click_add_room(self):
        """Clica no botão adicionar quarto"""
        self.click(self.ADD_ROOM_BUTTON)
    
    def click_edit_by_index(self, index):
        """Clica no botão editar do quarto por índice"""
        edit_buttons = self.find_elements(self.EDIT_BUTTONS)
        if index < len(edit_buttons):
            edit_buttons[index].click()
    
    def click_delete_by_index(self, index):
        """Clica no botão excluir do quarto por índice"""
        delete_buttons = self.find_elements(self.DELETE_BUTTONS)
        if index < len(delete_buttons):
            delete_buttons[index].click()


class RoomRegistrationPage(BasePage):
    """Page Object para registro de quartos"""
    
    # Locators
    NUMBER_FIELD = (By.ID, "numero")
    TYPE_FIELD = (By.ID, "tipo")
    CAPACITY_FIELD = (By.ID, "capacidade")
    PRICE_FIELD = (By.ID, "preco_diaria")
    STATUS_FIELD = (By.ID, "status")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "alert-success")
    ERROR_MESSAGE = (By.CLASS_NAME, "alert-danger")
    
    def __init__(self, driver, base_url="http://localhost:5000"):
        super().__init__(driver)
        self.base_url = base_url
        self.registration_url = f"{self.base_url}/admin/quarto/cadastro"
    
    def navigate(self):
        """Navega para página de registro de quarto"""
        self.go_to(self.registration_url)
        self.wait_for_page_load()
    
    def fill_form(self, room_data):
        """Preenche formulário de registro"""
        self.send_keys(self.NUMBER_FIELD, room_data.get("numero", ""))
        self.send_keys(self.TYPE_FIELD, room_data.get("tipo", ""))
        if room_data.get("capacidade"):
            self.select_dropdown(self.CAPACITY_FIELD, room_data["capacidade"])
        self.send_keys(self.PRICE_FIELD, str(room_data.get("preco_diaria", "")))
        if room_data.get("status"):
            self.select_dropdown(self.STATUS_FIELD, room_data["status"])
    
    def submit_form(self):
        """Submete o formulário"""
        self.click(self.SUBMIT_BUTTON)
    
    def register_room(self, room_data):
        """Processo completo de registro"""
        self.navigate()
        self.fill_form(room_data)
        self.submit_form()
    
    def get_success_message(self):
        """Obtém mensagem de sucesso"""
        return self.get_text(self.SUCCESS_MESSAGE)
    
    def get_error_message(self):
        """Obtém mensagem de erro"""
        return self.get_text(self.ERROR_MESSAGE)


class RoomEditPage(BasePage):
    """Page Object para edição de quartos"""
    
    # Locators
    NUMBER_FIELD = (By.ID, "numero")  # readonly
    TYPE_FIELD = (By.ID, "tipo")
    CAPACITY_FIELD = (By.ID, "capacidade")
    PRICE_FIELD = (By.ID, "preco_diaria")
    STATUS_FIELD = (By.ID, "status")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".btn-secondary")
    
    def __init__(self, driver, base_url="http://localhost:5000"):
        super().__init__(driver)
        self.base_url = base_url
    
    def fill_form(self, room_data):
        """Preenche formulário de edição"""
        if room_data.get("tipo"):
            self.send_keys(self.TYPE_FIELD, room_data["tipo"])
        if room_data.get("capacidade"):
            self.select_dropdown(self.CAPACITY_FIELD, room_data["capacidade"])
        if room_data.get("preco_diaria"):
            self.send_keys(self.PRICE_FIELD, str(room_data["preco_diaria"]))
        if room_data.get("status"):
            self.select_dropdown(self.STATUS_FIELD, room_data["status"])
    
    def submit_form(self):
        """Submete o formulário"""
        self.click(self.SUBMIT_BUTTON)
    
    def cancel_edit(self):
        """Cancela a edição"""
        self.click(self.CANCEL_BUTTON)
    
    def get_current_data(self):
        """Obtém dados atuais do formulário"""
        number_element = self.find_element(self.NUMBER_FIELD)
        type_element = self.find_element(self.TYPE_FIELD)
        price_element = self.find_element(self.PRICE_FIELD)
        
        return {
            "numero": number_element.get_attribute("value"),
            "tipo": type_element.get_attribute("value"),
            "preco_diaria": price_element.get_attribute("value")
        } 