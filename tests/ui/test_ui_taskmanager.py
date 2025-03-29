import pytest
from faker import Faker
import allure
from allure_commons.types import AttachmentType
from pages.registration_page import RegistrationPage
from pages.login_page import LoginPage
from pages.tasks_page import TasksPage

# Инициализация Faker для генерации тестовых данных
fake = Faker()

# Фикстура для инициализации драйвера
@pytest.fixture(scope="module")
def driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Настройки ChromeOptions
    options = Options()
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--headless")
    options.add_argument('--ignore-certificate-errors-spki-list') 
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--incognito") 
    options.add_argument("--window-size=1920,1080")
    options.binary_location = '/usr/bin/google-chrome-stable'  

    # Указываем путь к ChromeDriver
    service = Service('/usr/local/bin/chromedriver')

    # Инициализация драйвера с настройками
    driver = webdriver.Chrome(service=service, options=options)
    yield driver  
    driver.quit()  

# Фикстуры для инициализации страниц
@pytest.fixture
def registration_page(driver):
    return RegistrationPage(driver)

@pytest.fixture
def login_page(driver):
    return LoginPage(driver)

@pytest.fixture
def tasks_page(driver):
    return TasksPage(driver)

# Тест для регистрации и аутентификации пользователя
#@allure.feature("User Authentication")
@allure.story("End-to-End тестирование пользовательского интерфейса")
def test_user_registration_and_login(driver, registration_page, login_page, tasks_page):
    # Генерация тестовых данных
    username = fake.user_name()
    password = fake.password()

    with allure.step("1. Открытие страницы регистрации"):
        allure.attach(driver.get_screenshot_as_png(), name="Открытие страницы регистрации", attachment_type=AttachmentType.PNG)
        registration_page.get_register_page()  
    
    with allure.step("2. Регистрация нового пользователя"):
        allure.attach(driver.get_screenshot_as_png(), name="Регистрация нового пользователя", attachment_type=AttachmentType.PNG)
        registration_page.register_user(username, password) 

    with allure.step("3. Проверка успешной регистрации нового пользователя"):
        allure.attach(driver.get_screenshot_as_png(), name="Успешная регистрация", attachment_type=AttachmentType.PNG)
        tasks_page.verify_register_success()

    with allure.step("4. Авторизация зарегистрированного пользователя"):
        allure.attach(driver.get_screenshot_as_png(), name="Авторизация", attachment_type=AttachmentType.PNG)
        registration_page.login_user(username, password)

    with allure.step("5. Проверка успешной авторизации ранее зарегистрированного пользователя"):
        allure.attach(driver.get_screenshot_as_png(), name="Успешная авторизация", attachment_type=AttachmentType.PNG)
        tasks_page.verify_login_success()  

    with allure.step("5. Проверка того, что вошли под тем же пользователем, что и создали"):
        allure.attach(driver.get_screenshot_as_png(), name="Корректный пользователь", attachment_type=AttachmentType.PNG)
        tasks_page.verify_user_logged_in(username)

    with allure.step("6. Выход из системы"):
        allure.attach(driver.get_screenshot_as_png(), name="Выход из системы", attachment_type=AttachmentType.PNG)
        tasks_page.logout_user()

    with allure.step("6. Проверка того, что успешно вышли из системы"):
        allure.attach(driver.get_screenshot_as_png(), name="Успешный выхож", attachment_type=AttachmentType.PNG)
        tasks_page.verify_logout_success() 

        