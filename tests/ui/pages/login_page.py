from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    URL = "http://web:5000/login"

    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-testid='username-input']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-testid='password-input']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-testid='login-button']")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "[data-testid='success-message']")
    LOGIN_FORM = (By.CSS_SELECTOR, "form.login-form")  

    def get_login_page(self):
        self.open_url(self.URL)

    def enter_username(self, username):
        self.enter_text(self.USERNAME_INPUT, username)  

    def enter_password(self, password):
        self.enter_text(self.PASSWORD_INPUT, password)  

    def click_login(self):
        self.click_element(self.LOGIN_BUTTON)  

    def verify_login_success(self):
        return self.is_element_present(self.SUCCESS_MESSAGE)
        
    def verify_logout_success(self):
        return self.is_element_present(self.LOGIN_FORM)