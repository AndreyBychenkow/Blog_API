FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем PostgreSQL клиент
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Копируем проект
COPY . .

# Создаем директорию для логов
RUN mkdir -p logs

# Команда для запуска сервера
CMD ["gunicorn", "blog_project.wsgi:application", "--bind", "0.0.0.0:8000"] 