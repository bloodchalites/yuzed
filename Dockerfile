# Dockerfile (без расширения!)

# 1. Базовый образ
FROM python:3.11-slim

# 2. Рабочая директория
WORKDIR /app

# 3. Устанавливаем системные зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Копируем зависимости
COPY requirements.txt .

# 5. Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копируем весь код проекта
COPY . .

# 7. Создаем Django проект если его нет
RUN if [ ! -f "manage.py" ]; then \
    pip install Django==4.2.7 && \
    django-admin startproject config .; \
    fi

# 8. Запускаем сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]