import psycopg2
import os
import time
import allure


@allure.feature("Database Connection")
@allure.story("Test connection to PostgreSQL")
def test_database_connection():
    """Тест подключения к базе данных PostgreSQL"""
    db_params = {
        'dbname': os.environ.get('POSTGRES_DB', 'taskmanager'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'host': os.environ.get('POSTGRES_HOST', 'db'),
        'port': os.environ.get('POSTGRES_PORT', '5432')
    }

    max_retries = 5
    retry_interval = 2

    for attempt in range(max_retries):
        with allure.step(f"Попытка подключения {attempt+1}/{max_retries}"):
            try:
                allure.attach(str(db_params), name="Параметры подключения",
                              attachment_type=allure.attachment_type.TEXT)
                with allure.step("Установка соединения с базой данных"):
                    conn = psycopg2.connect(**db_params)

                with allure.step("Создание "
                                 "курсора и проверка версии PostgreSQL"):
                    cursor = conn.cursor()
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    allure.attach(str(version), name="Версия PostgreSQL",
                                  attachment_type=allure.attachment_type.TEXT)

                with allure.step("Получение списка таблиц"):
                    cursor.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                    """)
                    tables = cursor.fetchall()
                    allure.attach(str(tables),
                                  name="Список таблиц",
                                  attachment_type=allure.attachment_type.TEXT)

                if any(table[0] == 'task' for table in tables):
                    with allure.step("Проверка структуры таблицы task"):
                        cursor.execute("""
                            SELECT column_name, data_type
                            FROM information_schema.columns
                            WHERE table_name = 'task'
                        """)
                        columns = cursor.fetchall()
                        allure.attach(
                            str(columns),
                            name="Структура таблицы task",
                            attachment_type=allure.attachment_type.TEXT)

                    with allure.step(
                            "Проверка количества записей в таблице task"):
                        cursor.execute("SELECT COUNT(*) FROM task")
                        count = cursor.fetchone()[0]
                        allure.attach(
                            str(count),
                            name="Количество записей в таблице task",
                            attachment_type=allure.attachment_type.TEXT)

                    if count > 0:
                        with allure.step(
                                "Получение первых 5 записей из таблицы task"):
                            cursor.execute("""
                                SELECT id, title,
                                description, completed, user_id
                                FROM task
                                LIMIT 5
                            """)
                            tasks = cursor.fetchall()
                            allure.attach(
                                str(tasks),
                                name="Примеры задач",
                                attachment_type=allure.attachment_type.TEXT)

                with allure.step("Закрытие соединения с базой данных"):
                    cursor.close()
                    conn.close()

                with allure.step("Подключение к базе данных успешно"):
                    pass  # Здесь можно добавить дополнительное
                    # логирование или проверки

                return  # Тест прошёл успешно, выходим из функции

            except psycopg2.OperationalError as e:
                allure.attach(str(e),
                              name="Ошибка подключения",
                              attachment_type=allure.attachment_type.TEXT)
                if attempt < max_retries - 1:
                    with allure.step(f"Ошибка подключения,"
                                     f" повторная попытка через "
                                     f"{retry_interval} секунд"):
                        time.sleep(retry_interval)
                else:
                    with allure.step(
                            "Превышено максимальное количество"
                            " попыток подключения"):
                        raise
            except Exception as e:
                allure.attach(str(e),
                              name="Непредвиденная ошибка",
                              attachment_type=allure.attachment_type.TEXT)
                raise
