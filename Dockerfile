# --- Этап 1: Сборщик зависимостей ---
# Используем полную версию Python для установки зависимостей, включая компиляцию
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

# Устанавливаем системные зависимости, необходимые для psycopg2 и др.
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Копируем только файл с зависимостями и устанавливаем их
# Это кэширует слой с зависимостями, ускоряя последующие сборки
COPY requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Этап 2: Финальный образ ---
# Используем легкий образ для уменьшения размера
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем пользователя без прав root для безопасности
RUN addgroup --system app && adduser --system --group app

# Устанавливаем системные зависимости, необходимые для работы приложения
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

# Копируем установленные зависимости из сборщика
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Копируем исходный код приложения
COPY . .

# *** ВАЖНО: Собираем статические файлы ***
# Эта команда создаст директорию /home/app/staticfiles и необходимый манифест
RUN python manage.py collectstatic --no-input

# Меняем владельца файлов на созданного пользователя
RUN chown -R app:app /home/app

# Переключаемся на пользователя без прав root
USER app

# Открываем порт
EXPOSE 8000
