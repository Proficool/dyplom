from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

class TasksPage(BasePage):
    LOGOUT_BUTTON = (By.CSS_SELECTOR, '[data-testid="nav-logout"]')
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, '[data-testid="flash-message-success"]')
    LOGOUT_MESSAGE = (By.CSS_SELECTOR, '[data-testid="flash-message-info"]')
    
    def __init__(self, driver):
        super().__init__(driver)
         
    def verify_register_success(self):
        expected_url = "http://web:5000/login"
        self.wait_for_url(expected_url)  
        success_text_registr = self.get_element_text(self.SUCCESS_MESSAGE)
        assert success_text_registr == "Регистрация успешна! Теперь вы можете войти", \
            f"Ожидалось сообщение 'Регистрация успешна! Теперь вы можете войти', но получено: '{success_text}'"

    def verify_login_success(self):
        expected_url = "http://web:5000/tasks"
        self.wait_for_url(expected_url)  
        success_text_login = self.get_element_text(self.SUCCESS_MESSAGE)
        assert success_text_login == "Вы успешно вошли в систему", \
            f"Ожидалось сообщение 'Вы успешно вошли в систему', но получено: '{success_text}'"
        
    def verify_user_logged_in(self, expected_username):
        logout_button_text = self.get_element_text(self.LOGOUT_BUTTON)
        expected_logout_button_text = f"Выйти ({expected_username})"
        assert logout_button_text == expected_logout_button_text, (
            f"Некорректный текст кнопки 'Выйти':\n {logout_button_text}\n",
            f"Ожидалось:\n {expected_logout_button_text}"
            )
    
    def logout_user(self):
        self.click_element(self.LOGOUT_BUTTON)
        expected_url = "http://web:5000/login"
        self.wait_for_url(expected_url)  
        
    def verify_logout_success(self):
        logout_message_text = self.get_element_text(self.LOGOUT_MESSAGE)
        assert logout_message_text == "Вы вышли из системы", \
            f"Ожидалось сообщение 'Вы вышли из системы', но получено: '{logout_message_text}'"

    