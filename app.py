from flask import (Flask, render_template, request,
                   redirect, url_for, flash, session, jsonify)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import time
import psycopg2
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get(
        'DATABASE_URL', 'postgresql://postgres:postgres@db:5432/taskmanager')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Ожидание доступности базы данных
def wait_for_db(max_retries=30, retry_interval=2):
    """Ожидание доступности базы данных перед запуском приложения"""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    # Извлечение параметров подключения из URI
    if db_uri.startswith('postgresql://'):
        # Примерный формат: postgresql://username:password@host:port/dbname
        parts = db_uri.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        host_port = host_db[0].split(':')

        dbname = host_db[1]
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'

        retry_count = 0
        while retry_count < max_retries:
            try:
                print(
                    f"Попытка подключения к базе данных ("
                    f"попытка {retry_count+1}/{max_retries})..."
                )
                conn = psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port
                )
                conn.close()
                print("Подключение к базе данных успешно установлено!")
                return True
            except psycopg2.OperationalError as e:
                print(f"Не удалось подключиться к базе данных: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Повторная попытка через "
                          f"{retry_interval} секунд...")
                    time.sleep(retry_interval)
                else:
                    print(
                        "Превышено максимальное количество "
                        "попыток подключения к базе данных.")
                    return False
    return True


# Ожидание готовности базы данных перед инициализацией приложения
wait_for_db()

db = SQLAlchemy(app)


# Модели
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Настройка Swagger UI
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Менеджер задач API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Маршрут для доступа к документации API без авторизации
@app.route('/api/documentation')
def api_documentation():
    return redirect(SWAGGER_URL)


# Создание базы данных
with app.app_context():
    db.create_all()

    # Копируем swagger.json в статическую директорию
    os.makedirs('static', exist_ok=True)
    with open('swagger.json', 'r') as f:
        swagger_data = json.load(f)
    with open('static/swagger.json', 'w') as f:
        json.dump(swagger_data, f)


# Проверка авторизации
def login_required(view):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'danger')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view


# Проверка авторизации для API
def api_login_required(view):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Требуется авторизация'}), 401
        return view(*args, **kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view


# Маршруты для авторизации
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Если пользователь уже авторизован, перенаправляем на главную
    if 'user_id' in session:
        return redirect(url_for('tasks'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Валидация данных
        errors = {}

        if not username:
            errors['username'] = 'Имя пользователя обязательно'
        elif len(username) < 3:
            errors['username'] = ('Имя пользователя должно '
                                  'содержать не менее 3 символов')
        elif len(username) > 20:
            errors['username'] = ('Имя пользователя должно'
                                  ' содержать не более 20 символов')
        elif not username.isalnum() and '_' not in username:
            errors['username'] = ('Имя пользователя может содержать только'
                                  ' буквы, цифры и символ подчеркивания')

        if not password:
            errors['password'] = 'Пароль обязателен'
        elif len(password) < 6:
            errors['password'] = 'Пароль должен содержать не менее 6 символов'

        # Проверка существования пользователя
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            errors['username'] = 'Пользователь с таким именем уже существует'

        # Если есть ошибки, возвращаем их
        if errors:
            for field, message in errors.items():
                flash(f'{message}', 'danger')
            return render_template('register.html')

        # Создание нового пользователя
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        # Используем 303 See Other
        # для предотвращения повторной отправки формы при обновлении
        return redirect(url_for('login'), code=303)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Если пользователь уже авторизован, перенаправляем на главную
    if 'user_id' in session:
        return redirect(url_for('tasks'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Валидация данных
        errors = {}

        if not username:
            errors['username'] = 'Имя пользователя обязательно'

        if not password:
            errors['password'] = 'Пароль обязателен'

        # Если есть ошибки валидации, возвращаем их
        if errors:
            for field, message in errors.items():
                flash(f'{message}', 'danger')
            return render_template('login.html')

        # Проверка учетных данных
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Вы успешно вошли в систему', 'success')
            # Используем 303 See Other
            # для предотвращения повторной отправки формы при обновлении
            return redirect(url_for('tasks'), code=303)
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


# CRUD операции для задач
@app.route('/tasks')
@login_required
def tasks():
    user_tasks = Task.query.filter_by(
        user_id=session['user_id']).order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=user_tasks)


@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        # Валидация данных
        errors = {}

        if not title:
            errors['title'] = 'Название задачи обязательно'
        elif len(title) > 100:
            errors['title'] = ('Название задачи'
                               ' должно содержать не более 100 символов')

        # Если есть ошибки, возвращаем их
        if errors:
            for field, message in errors.items():
                flash(f'{message}', 'danger')
            return render_template('create_task.html')

        new_task = Task(
            title=title,
            description=description,
            user_id=session['user_id']
        )

        db.session.add(new_task)
        db.session.commit()

        flash('Задача успешно создана', 'success')
        # Используем 303 See Other для
        # предотвращения повторной отправки формы при обновлении
        return redirect(url_for('tasks'), code=303)

    return render_template('create_task.html')


@app.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        flash('У вас нет доступа к этой задаче', 'danger')
        return redirect(url_for('tasks'))

    return render_template('view_task.html', task=task)


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        flash('У вас нет доступа к этой задаче', 'danger')
        return redirect(url_for('tasks'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        completed = 'completed' in request.form

        # Валидация данных
        errors = {}

        if not title:
            errors['title'] = 'Название задачи обязательно'
        elif len(title) > 100:
            errors['title'] = \
                'Название задачи должно содержать не более 100 символов'

        # Если есть ошибки, возвращаем их
        if errors:
            for field, message in errors.items():
                flash(f'{message}', 'danger')
            return render_template('edit_task.html', task=task)

        task.title = title
        task.description = description
        task.completed = completed

        db.session.commit()

        flash('Задача успешно обновлена', 'success')
        # Используем 303 See Other для
        # предотвращения повторной отправки формы при обновлении
        return redirect(url_for('tasks'), code=303)

    return render_template('edit_task.html', task=task)


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        flash('У вас нет доступа к этой задаче', 'danger')
        return redirect(url_for('tasks'))

    db.session.delete(task)
    db.session.commit()

    flash('Задача успешно удалена', 'success')
    # Используем 303 See Other для
    # предотвращения повторной отправки формы при обновлении
    return redirect(url_for('tasks'), code=303)


@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        flash('У вас нет доступа к этой задаче', 'danger')
        return redirect(url_for('tasks'))

    task.completed = not task.completed
    db.session.commit()

    status = "выполнена" if task.completed else "не выполнена"
    flash(f'Задача отмечена как {status}', 'success')
    # Используем 303 See Other
    # для предотвращения повторной отправки формы при обновлении
    return redirect(url_for('tasks'), code=303)


# API маршруты для авторизации
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify(
            {'error': 'Необходимо указать имя пользователя и пароль'}), 400

    username = data['username']
    password = data['password']

    # Проверка существования пользователя
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify(
            {'error': 'Пользователь с таким именем уже существует'}), 400

    # Создание нового пользователя
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Регистрация успешна'}), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify(
            {'error': 'Необходимо указать имя пользователя и пароль'}), 400

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'message': 'Вы успешно вошли в систему',
            'user_id': user.id,
            'username': user.username
        }), 200
    else:
        return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401


# API маршруты для задач
@app.route('/api/tasks', methods=['GET'])
@api_login_required
def api_get_tasks():
    user_tasks = (
        Task.query.filter_by(user_id=session['user_id']).order_by(
            Task.created_at.desc()).all())
    tasks_list = []
    for task in user_tasks:
        tasks_list.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'created_at': task.created_at.isoformat(),
            'completed': task.completed,
            'user_id': task.user_id
        })
    return jsonify(tasks_list)


@app.route('/api/tasks', methods=['POST'])
@api_login_required
def api_create_task():
    data = request.get_json()

    # Убрана проверка на наличие title
    # if not data or 'title' not in data:
    #     return jsonify({'error': 'Название задачи обязательно'}), 400

    new_task = Task(
        title=data.get('title', ''),  # Позволяет пустой title
        description=data.get('description', ''),
        completed=data.get('completed', False),
        user_id=session['user_id']
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        'id': new_task.id,
        'title': new_task.title,
        'description': new_task.description,
        'created_at': new_task.created_at.isoformat(),
        'completed': new_task.completed,
        'user_id': new_task.user_id
    }), 201


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@api_login_required
def api_get_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        return jsonify({'error': 'У вас нет доступа к этой задаче'}), 403

    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'created_at': task.created_at.isoformat(),
        'completed': task.completed,
        'user_id': task.user_id
    })


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@api_login_required
def api_update_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        return jsonify({'error': 'У вас нет доступа к этой задаче'}), 403

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Данные не предоставлены'}), 400

    if 'title' in data:
        if not data['title']:
            return jsonify(
                {'error': 'Название задачи не может быть пустым'}), 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'completed' in data:
        task.completed = data['completed']

    db.session.commit()

    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'created_at': task.created_at.isoformat(),
        'completed': task.completed,
        'user_id': task.user_id
    })


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@api_login_required
def api_delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        return jsonify({'error': 'У вас нет доступа к этой задаче'}), 403

    db.session.delete(task)
    db.session.commit()

    return '', 204


@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
@api_login_required
def api_toggle_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Проверка, принадлежит ли задача текущему пользователю
    if task.user_id != session['user_id']:
        return jsonify({'error': 'У вас нет доступа к этой задаче'}), 403

    task.completed = not task.completed
    db.session.commit()

    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'created_at': task.created_at.isoformat(),
        'completed': task.completed,
        'user_id': task.user_id
    })


if __name__ == '__main__':
    app.run(debug=True, port=8080)
