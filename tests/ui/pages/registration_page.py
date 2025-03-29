from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class RegistrationPage(BasePage):
    # URL для страницы регистрации
    URL = "http://web:5000/register"

    # Локаторы
    USERNAME_INPUT = (By.CSS_SELECTOR, '[data-testid="username-input"]')
    PASSWORD_INPUT = (By.CSS_SELECTOR, '[data-testid="password-input"]')
    REGISTRATION_BUTTON = (By.CSS_SELECTOR, '[data-testid="register-button"]')
    LOGIN_BUTTON = (By.CSS_SELECTOR, '[data-testid="login-button"]')
    LOGOUT_BUTTON = (By.CSS_SELECTOR, '[data-testid="nav-logout"]')

    def __init__(self, driver):
        super().__init__(driver)
        self.url = "http://web:5000/register"  

    # Регистрирует нового пользователя
    def register_user(self, username, password):
        self.enter_text(self.USERNAME_INPUT, username)
        self.enter_text(self.PASSWORD_INPUT, password)
        # Нажимаем кнопку регистрации
        self.click_element(self.REGISTRATION_BUTTON)

    # Авторизует созданного пользователя
    def login_user(self, username, password):
        self.enter_text(self.USERNAME_INPUT, username)
        self.enter_text(self.PASSWORD_INPUT, password)
        self.click_element(self.LOGIN_BUTTON)

    def get_register_page(self):
        self.open_url(self.URL)

    def enter_username(self, username):
        self.enter_text(self.USERNAME_INPUT, username)

    def enter_password(self, password):
        self.enter_text(self.PASSWORD_INPUT, password)

    def click_register(self):
        self.click_element(self.REGISTRATION_BUTTON)

    def click_login(self):
        self.click_element(self.LOGIN_BUTTON)

    def click_logout(self):
        self.click_element(self.LOGOUT_BUTTON)

    