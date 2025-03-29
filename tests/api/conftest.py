import pytest
import psycopg2
import requests
import allure

# Параметры подключения к БД
DB_PARAMS = {
    "dbname": "taskmanager",
    "user": "postgres",
    "password": "postgres",
    "host": "db",
    "port": "5432"
}

# Фикстура для базового URL API
@pytest.fixture(scope="session")
def base_url():
    """Возвращает базовый URL API."""
    return "http://web:5000"  

# Фикстура для подключения к базе данных
@pytest.fixture(scope="session")
def db_connection():
    """Возвращает подключение к базе данных."""
    conn = psycopg2.connect(**DB_PARAMS)
    yield conn
    conn.close()

# Фикстура для очистки базы данных перед всеми тестами
@pytest.fixture(scope="function", autouse=True)
def cleanup_before_tests(db_connection):
    with allure.step("Очистка базы данных перед всеми тестами"):
        cursor = db_connection.cursor()
        cursor.execute('DELETE FROM task WHERE user_id IS NOT NULL')
        cursor.execute('DELETE FROM "user"')
        db_connection.commit()
        cursor.close()

# Фикстура для очистки базы данных после всех тестов
@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests(db_connection):
    yield
    with allure.step("Очистка базы данных после всех тестов"):
        cursor = db_connection.cursor()
        cursor.execute('DELETE FROM task WHERE user_id IS NOT NULL')
        cursor.execute('DELETE FROM "user"')
        db_connection.commit()
        cursor.close()

# Фикстура для регистрации пользователя
@pytest.fixture
def register_user(base_url, db_connection):
    username = "testuser1"
    password = "testpass1"
    user_data = {"username": username, "password": password}
    response = requests.post(f"{base_url}/api/register", json=user_data)
    yield username, password

# Фикстура для авторизации пользователя
@pytest.fixture
def login_user(base_url, register_user):
    username, password = register_user
    login_data = {"username": username, "password": password}
    response = requests.post(f"{base_url}/api/login", json=login_data)
    yield response.cookies

# Функция для проверки наличия пользователя в базе данных
def check_user_in_db(username, db_connection):
    cursor = db_connection.cursor()
    cursor.execute('SELECT 1 FROM "user" WHERE username = %s', (username,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None