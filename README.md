# Менеджер задач

Веб-приложение для управления личными задачами с REST API и веб-интерфейсом.

## Описание проекта Диплом

Менеджер задач - это веб-приложение, разработанное на Flask, которое позволяет пользователям регистрироваться, входить в систему и управлять своими задачами. Приложение предоставляет как веб-интерфейс, так и REST API для взаимодействия с задачами.

### Основные функции

- **Аутентификация пользователей**:
  - Регистрация новых пользователей
  - Вход в систему
  - Выход из системы

- **Управление задачами**:
  - Создание новых задач
  - Просмотр списка задач
  - Просмотр детальной информации о задаче
  - Редактирование задач
  - Удаление задач
  - Отметка задач как выполненных/невыполненных

- **REST API**:
  - Полный доступ к функциональности через API
  - Документация API через Swagger UI

## Технический стек

- **Backend**: Python, Flask
- **База данных**: PostgreSQL
- **ORM**: SQLAlchemy
- **Frontend**: HTML, CSS, Bootstrap 5
- **API документация**: Swagger UI
- **Контейнеризация**: Docker
- **Тестирование**: Pytest, Selenium, Allure

## Структура проекта

- `app.py` - основной файл приложения
- `templates/` - HTML шаблоны
- `static/` - статические файлы
- `swagger.json` - документация API
- `Dockerfile` - инструкции для сборки Docker-образа
- `Dockerfile.test` - инструкции для сборки Docker-образа для тестирования
- `docker-compose.yml` - конфигурация Docker Compose
- `requirements.txt` - зависимости Python
- `tests/` - автоматизированные тесты
- `Jenkinsfile` - конфигурация CI/CD для Jenkins

## Запуск приложения

### Запуск с использованием Docker (рекомендуется)

1. Убедитесь, что у вас установлены Docker и Docker Compose:
   ```
   docker --version
   docker-compose --version
   ```

2. Клонируйте репозиторий:
   ```
   git clone https://github.com/lvslove/flask.git
   ```

3. Соберите и запустите контейнеры:
   ```
   docker-compose build
   docker-compose up -d
   ```

4. Приложение будет доступно по адресу: http://localhost:5000

5. Для остановки приложения:
   ```
   docker-compose down
   ```

### Запуск без Docker

1. Убедитесь, что у вас установлен Python 3.9 или выше:
   ```
   python --version
   ```

2. Клонируйте репозиторий:
   ```
   git clone <URL репозитория>
   cd <директория проекта>
   ```

3. Создайте и активируйте виртуальное окружение:
   ```
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows
   ```

4. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

5. Настройте переменные окружения для подключения к PostgreSQL:
   ```
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taskmanager
   ```

6. Запустите приложение:
   ```
   flask run --port=5000
   ```

7. Приложение будет доступно по адресу: http://localhost:5000

## Запуск тестов

### Запуск тестов с использованием Docker

1. Запуск всех сервисов (приложение, база данных и тесты):
   ```
   docker-compose up
   ```

2. Запуск только тестов (если приложение и база данных уже запущены):
   ```
   docker-compose up test
   ```

3. Запуск конкретных тестов:
   ```
   # Тесты подключения к базе данных
   docker-compose run --rm test

   # API тесты
   docker-compose run --rm -e TEST_PATH=tests/api/ test

   # UI тесты
   docker-compose run --rm -e TEST_PATH=tests/ui/ test

   # Конкретный тест с дополнительными аргументами
   docker-compose run --rm -e TEST_PATH=tests/api/test_task_lifecycle.py -e TEST_ARGS="-k test_create_task" test

   # Тест с allure reports 
   docker compose run --rm -e TEST_ARGS=--alluredir=test-results test

   allure generate test-results -o allure-report --clean

   allure open allure-report
   ```

### Запуск тестов без Docker

1. Установите дополнительные зависимости для тестирования:
   ```
   pip install -r tests/requirements.txt
   ```

2. Запустите тесты:
   ```
   # Все тесты
   pytest tests/

   # Тесты API
   pytest tests/api/

   # Тесты UI
   pytest tests/ui/

   # Конкретный тест
   pytest tests/api/test_task_lifecycle.py -k test_create_task
   ```

## Использование API

### Документация API

Документация API доступна по адресу: http://localhost:5000/api/docs

### Примеры запросов к API

#### Регистрация нового пользователя
```
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```

#### Вход в систему
```
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}' \
  -c cookies.txt
```

#### Получение списка задач
```
curl -X GET http://localhost:5000/api/tasks \
  -b cookies.txt
```

#### Создание новой задачи
```
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "Новая задача", "description": "Описание задачи"}'
```

#### Получение задачи по ID
```
curl -X GET http://localhost:5000/api/tasks/1 \
  -b cookies.txt
```

#### Обновление задачи
```
curl -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "Обновленная задача", "description": "Новое описание", "completed": true}'
```

#### Удаление задачи
```
curl -X DELETE http://localhost:5000/api/tasks/1 \
  -b cookies.txt
```

#### Переключение статуса задачи
```
curl -X POST http://localhost:5000/api/tasks/1/toggle \
  -b cookies.txt
```

## Безопасность

- Пароли хешируются с использованием Werkzeug Security
- Проверка авторизации для всех защищенных маршрутов
- Проверка принадлежности задач текущему пользователю

## Разработка и тестирование

### Запуск в режиме отладки

```
FLASK_DEBUG=1 flask run --port=5000
```

### Непрерывная интеграция

Проект настроен для непрерывной интеграции с использованием Jenkins. При каждом коммите в репозиторий автоматически запускаются тесты и генерируются отчеты Allure.

### Структура тестов

- `tests/api/` - тесты REST API
- `tests/ui/` - тесты пользовательского интерфейса
- `tests/test_db_connection.py` - тесты подключения к базе данных

Подробная информация о тестировании доступна в файле `README_TESTING.md`.
