# Бэкенд для блога

API для управления блогом с функциями регистрации, аутентификации, CRUD для статей, комментариев и категорий.

## ✨ Основные технологии

- Python 3.10+
- Django 5.x
- Django Ninja (для создания API)
- Django Ninja JWT (для JWT аутентификации)
- PostgreSQL (в Docker-конфигурации)
- Structlog (для структурированного логирования)
- Docker & Docker Compose

## 🚀 Функционал

- Регистрация и аутентификация пользователей (JWT).
- CRUD операции для статей (создание, чтение, обновление, удаление).
- CRUD операции для комментариев к статьям.
- Управление категориями статей (для администраторов).
- Встроенная документация API (Swagger UI).

## 🐳 Запуск проекта с использованием Docker (Рекомендуемый способ)

### Предварительные требования
- Docker
- Docker Compose

### Шаги для запуска
1.  **Клонировать репозиторий:**
    ```bash
    git clone https://github.com/AndreyBychenkow/Blog_API.git
    cd Blog_API
    ```

2.  **Создать `.env` файл:**
    Создайте `.env` вручную в корне проекта со следующими переменными:
    ```env
    DEBUG=True
    SECRET_KEY=your-very-secret-django-key-in-production
    
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=blog_db
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432
    
    ACCESS_TOKEN_LIFETIME_MINUTES=5
    REFRESH_TOKEN_LIFETIME_DAYS=1
    ```

3.  **Запустить Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```
    Флаг `--build` пересобирает образы, если были изменения в `Dockerfile` или коде.

4.  **Применить миграции базы данных:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Создать суперпользователя (для доступа к Django Admin):**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Следуйте инструкциям в консоли.

6.  **Доступ к приложению:**
    - API: [http://localhost:8000/api/](http://localhost:8000/api/)
    - Документация API (Swagger): [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
    - Django Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Полезные команды Docker Compose
- Просмотр логов всех сервисов: `docker-compose logs -f`
- Просмотр логов конкретного сервиса: `docker-compose logs -f web`
- Остановка контейнеров: `docker-compose down`
- Остановка и удаление volume'ов (данные БД будут удалены!): `docker-compose down -v`

## 🛠️ Локальная разработка (без Docker)

### Предварительные требования
- Python 3.10+
- Pip
- (Опционально, но рекомендуется) PostgreSQL сервер

### Шаги для запуска
1.  **Клонировать репозиторий** (см. выше).

2.  **Создать и активировать виртуальное окружение:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/MacOS
    source venv/bin/activate
    ```

3.  **Установить зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Настроить переменные окружения:**
    Создайте файл `.env` (см. секцию Docker) или установите переменные окружения в вашей системе. Для локальной разработки можно использовать SQLite.
    Пример для SQLite:
    ```env
    DEBUG=True
    SECRET_KEY=your-local-secret-key
    DB_ENGINE=django.db.backends.sqlite3
    DB_NAME=db.sqlite3 
    ```

5.  **Применить миграции:**
    ```bash
    python manage.py migrate
    ```

6.  **Создать суперпользователя:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Запустить сервер разработки Django:**
    ```bash
    python manage.py runserver
    ```
    Приложение будет доступно по адресу [http://localhost:8000/](http://localhost:8000/).

