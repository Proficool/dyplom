import requests
import allure
import pytest
import pytest_check as check
from conftest import check_user_in_db, register_user, login_user

@allure.story("Тестирование API успешной регистрации пользователя")
def test_user_registration(base_url, db_connection):
    with allure.step("Генерирование тестовых данных"):
        username = "Vitaliy"
        password = "012345"

    with allure.step("Подготовка тестовых данных"):
        user_data = {"username": username, "password": password}

    with allure.step("Регистрация пользователя (должна быть успешной)"):
        response = requests.post(f"{base_url}/api/register", json=user_data)
        check.equal(response.status_code, 201)
        check.equal(response.json().get("message"), "Регистрация успешна")
        check.is_true(check_user_in_db(username, db_connection))

        print("Response status:", response.status_code)
        print("Response JSON:", response.json())
        print(f"User {username} exists in DB: {check_user_in_db(username, db_connection)}")   

@allure.story("Тестирование API попытки регистрации существующего пользователя")
def test_existing_user_registration(base_url, db_connection, register_user):
    with allure.step("Подготовка тестовых данных"):
        username, password = register_user

    with allure.step("Попытка регистрации существующего пользователя (должна завершиться ошибкой)"):
        user_data = {"username": username, "password": password}
        response = requests.post(f"{base_url}/api/register", json=user_data)
        check.equal(response.status_code, 400)
        check.equal(response.json().get("error"), "Пользователь с таким именем уже существует")
        check.is_true(check_user_in_db(username, db_connection))
        
        print("Response status:", response.status_code)
        print("Response JSON:", response.json())
        print(f"User {username} exists in DB: {check_user_in_db(username, db_connection)}")
                

def get_test_data():
    with allure.step("Генерирование тестовых данных"):
        return [
            ({"username": "", "password": "testpass2"}, 400, "Неверный запрос"),
            ({"username": "testuser2", "password": ""}, 400, "Неверный запрос"),
            ({"username": "", "password": ""}, 400, "Неверный запрос"),
        ]

@pytest.mark.parametrize("test_data, expected_status, expected_message", get_test_data())
@allure.story("Тестирование API негативных сценариев регистрации")
def test_invalid_registration(base_url, test_data, expected_status, expected_message, db_connection):
    with allure.step("Подготовка тестовых данных"):
        user_data = test_data.copy()

    with allure.step("Отправка запроса на регистрацию пользователя"):
        response = requests.post(f"{base_url}/api/register", json=user_data)
        print(response.status_code)
        print(response.json())
        check.equal(response.status_code, expected_status)
        check.equal(response.json().get("error"), expected_message)

    with allure.step("Проверка наличия пользователя в базе данных"):
        if expected_status == 400 and user_data.get("username"):
            user_exists = check_user_in_db(user_data["username"], db_connection)
            check.is_false(user_exists)

    with allure.step("Проверка попадания пользователя в БД"):
        username = user_data.get("username")
        if username:  # Проверяем, если вообще передавалось имя пользователя
            user_exists = check_user_in_db(username, db_connection)
            print(f"Пользователь '{username}' в БД: {user_exists}")
            check.is_false(user_exists, "Ошибка! Некорректный пользователь записался в БД")


@allure.story("Тестирование API авторизации пользователя") 
def test_user_login(base_url, register_user, db_connection):
    with allure.step("Подготовка тестовых данных"):
        username, password = register_user

    with allure.step("Авторизация пользователя"):
        login_data = {"username": username, "password": password}
        login_response = requests.post(f"{base_url}/api/login", json=login_data)
        check.equal(login_response.status_code, 200)
        check.equal(login_response.json().get("message"), "Вы успешно вошли в систему")
        check.is_true(check_user_in_db(username, db_connection))  

@allure.story("Тестирование API авторизации незарегистрированного пользователя") 
def test_user_login_without_reg(base_url, db_connection):
    with allure.step("Попытка авторизации незарегистрированного пользователя"):
        login_data = {"username": "unknownuser", "password": "unknownpass"}
        login_response = requests.post(f"{base_url}/api/login", json=login_data)
        check.equal(login_response.status_code, 401)
        check.equal(login_response.json().get("error"), "Неверное имя пользователя или пароль")
        username = login_data["username"]
        check.is_false(check_user_in_db(username, db_connection))

@allure.story("Тестирование работы с задачами Backend API")
def test_work_with_task(base_url, db_connection, login_user):
    cookies = login_user

    with allure.step("Создание новой задачи"):
        task_data = {"title": "Test Task", "description": "This is a test task"}
        create_response = requests.post(f"{base_url}/api/tasks", json=task_data, cookies=cookies)
        check.equal(create_response.status_code, 201)

    with allure.step("Проверка данных задачи в базе данных"):
        response_data = create_response.json()
        task_id = response_data["id"]
        cursor = db_connection.cursor()
        cursor.execute("SELECT id, title, description FROM task WHERE id = %s", (task_id,))
        task_from_db = cursor.fetchone()
        check.is_not_none(task_from_db)
        db_task_id, db_title, db_description = task_from_db
        check.equal(db_task_id, task_id)
        check.equal(db_title, "Test Task")
        check.equal(db_description, "This is a test task")

    with allure.step("Обновление задачи"):
        update_data = {"title": "Updated Task", "description": "This is an updated task"}
        update_response = requests.put(f"{base_url}/api/tasks/{task_id}", json=update_data, cookies=cookies)
        check.equal(update_response.status_code, 200)

    with allure.step("Проверка обновленных данных в базе данных"):
        cursor.execute("SELECT title, description FROM task WHERE id = %s", (task_id,))
        db_title, db_description = cursor.fetchone()
        check.equal(db_title, "Updated Task")
        check.equal(db_description, "This is an updated task")

    with allure.step("Изменение статуса задачи"):
        update_status_data = {"completed": True}
        status_response = requests.put(f"{base_url}/api/tasks/{task_id}", json=update_status_data, cookies=cookies)
        check.equal(status_response.status_code, 200)

    with allure.step("Проверка статуса задачи в базе данных"):
        cursor.execute("SELECT completed FROM task WHERE id = %s", (task_id,))
        db_completed = cursor.fetchone()[0]
        check.is_true(db_completed)

    with allure.step("Удаление задачи"):
        delete_response = requests.delete(f"{base_url}/api/tasks/{task_id}", cookies=cookies)
        check.equal(delete_response.status_code, 204)

    with allure.step("Проверка удаления задачи из базы данных"):
        cursor.execute("SELECT id FROM task WHERE id = %s", (task_id,))
        check.is_none(cursor.fetchone())