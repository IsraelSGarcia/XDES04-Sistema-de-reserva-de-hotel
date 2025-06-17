"""
Performance helpers para acelerar testes E2E
Substitui time.sleep() por waits inteligentes
"""
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def smart_wait_for_page_load(driver, timeout=3):
    """Aguarda página carregar de forma inteligente (mais rápido que sleep)"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except:
        pass  # Se falhar, continua mesmo assim


def smart_wait_for_url_change(driver, expected_url_part, timeout=3):
    """Aguarda mudança de URL de forma inteligente"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: expected_url_part in d.current_url
        )
        return True
    except:
        return False


def smart_wait_for_element(driver, locator, timeout=3):
    """Aguarda elemento aparecer de forma inteligente"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return True
    except:
        return False


def smart_wait_for_text_in_page(driver, text, timeout=3):
    """Aguarda texto aparecer na página"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: text.lower() in d.page_source.lower()
        )
        return True
    except:
        return False


def quick_sleep(seconds=0.1):
    """Sleep muito rápido apenas quando necessário"""
    time.sleep(seconds)


def turbo_wait_for_navigation(driver, timeout=2):
    """Aguarda navegação ultra-rápida"""
    try:
        # Aguarda apenas que a página tenha algum conteúdo
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.page_source) > 100
        )
    except:
        pass  # Se falhar, continua 