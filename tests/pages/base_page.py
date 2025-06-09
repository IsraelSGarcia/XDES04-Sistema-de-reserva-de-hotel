"""
Page Object base com métodos comuns para todos os page objects
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time


class BasePage:
    """Classe base para Page Objects"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def go_to(self, url):
        """Navega para uma URL"""
        self.driver.get(url)
    
    def find_element(self, locator):
        """Encontra um elemento com espera explícita"""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator):
        """Encontra múltiplos elementos"""
        return self.driver.find_elements(*locator)
    
    def click(self, locator):
        """Clica em um elemento com espera de clicabilidade"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def send_keys(self, locator, text):
        """Envia texto para um campo"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator):
        """Obtém texto de um elemento"""
        element = self.find_element(locator)
        return element.text
    
    def select_dropdown(self, locator, value):
        """Seleciona opção em dropdown"""
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_value(value)
    
    def wait_for_url_contains(self, url_part):
        """Aguarda URL conter determinado texto"""
        return self.wait.until(EC.url_contains(url_part))
    
    def wait_for_element_visible(self, locator):
        """Aguarda elemento ficar visível"""
        return self.wait.until(EC.visibility_of_element_located(locator))
    
    def is_element_present(self, locator):
        """Verifica se elemento está presente"""
        try:
            self.driver.find_element(*locator)
            return True
        except:
            return False
    
    def get_alert_text_and_accept(self):
        """Obtém texto do alert e aceita"""
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text
    
    def scroll_to_element(self, locator):
        """Rola página até elemento"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
    
    def wait_for_page_load(self):
        """Aguarda carregamento completo da página"""
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        time.sleep(0.5)  # Pequena pausa adicional 