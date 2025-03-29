from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open_url(self, url):
        self.driver.get(url)

    def find_element(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def click_element(self, locator, timeout=10):
        self.find_element(locator, timeout).click()

    def enter_text(self, locator, text, timeout=10):
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        
    # def is_element_present(self, locator, timeout=10):
    #     try:
    #         self.find_element(locator, timeout)
    #         return True
    #     except:
    #         return False
            
    # def wait_for_element_visible(self, locator, timeout=10):
    #     return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
        
    def get_element_text(self, locator, timeout=10):
        return self.find_element(locator, timeout).text

    def wait_for_url(self, expected_url, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.current_url == expected_url
    )

    