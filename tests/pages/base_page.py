"""
Page Object base com métodos comuns para todos os page objects
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException


class BasePage:
    """Classe base para Page Objects"""
    
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
    
    def go_to(self, url):
        """Navega para uma URL"""
        self.driver.get(url)
    
    def find_element(self, locator):
        """Encontra um elemento"""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator):
        """Encontra múltiplos elementos"""
        return self.driver.find_elements(*locator)
    
    def click(self, locator):
        """Clica em um elemento com tratamento de interceptação"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        
        # Tenta scroll para elemento visível
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)  # Aguarda scroll completar
        
        try:
            element.click()
        except ElementClickInterceptedException:
            # Se interceptado, tenta JavaScript click
            self.driver.execute_script("arguments[0].click();", element)
    
    def send_keys(self, locator, text):
        """Digita texto em um campo"""
        element = self.wait.until(EC.presence_of_element_located(locator))
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator):
        """Obtém o texto de um elemento"""
        element = self.find_element(locator)
        return element.text
    
    def select_dropdown(self, locator, value):
        """Seleciona uma opção em dropdown"""
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_value(value)
    
    def wait_for_url_contains(self, url_part):
        """Aguarda URL conter determinado texto"""
        return self.wait.until(EC.url_contains(url_part))
    
    def wait_for_element_visible(self, locator, timeout=None):
        """Aguarda elemento ficar visível"""
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.visibility_of_element_located(locator))
    
    def is_element_present(self, locator):
        """Verifica se um elemento está presente"""
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
        """Faz scroll até o elemento"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
    
    def wait_for_page_load(self):
        """Aguarda o carregamento da página"""
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        time.sleep(0.5)  # Pequena pausa adicional 