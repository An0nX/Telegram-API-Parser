# Анализатор Telegram-каналов | Telegram Channel Analyzer

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20+-2496ED?style=for-the-badge&logo=docker&logoColor=white)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Docker Pulls](https://img.shields.io/docker/pulls/whn0thacked/telegram-api-parser?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/whn0thacked/telegram-api-parser)

Веб-сервис с REST API для асинхронного сбора и анализа статистики публичных Telegram-каналов. Он использует **Telethon** для взаимодействия с Telegram API и **Celery** для фоновой обработки задач, что позволяет запускать длительные анализы без блокировки основного процесса.

## 🚀 Основные возможности

*   **Асинхронный анализ:** Задачи по сбору данных выполняются в фоновом режиме, не заставляя клиента ждать.
*   **REST API:** Удобный интерфейс для интеграции с другими сервисами или фронтенд-приложениями.
*   **Расчет ключевых метрик:** Автоматически вычисляет ER (Engagement Rate), CPV (Cost Per View), CPM (Cost Per Mille), средние и общие показатели просмотров/реакций.
*   **Гибкая настройка:** Возможность задавать период анализа (в днях) и стоимость поста для расчета метрик.
*   **Простое развертывание:** Проект полностью контейнеризирован и доступен как готовый образ на Docker Hub.

## 📦 Установка и запуск

Выберите один из двух способов в зависимости от вашей цели.

---

### Способ 1: Быстрый запуск из Docker Hub

Этот способ идеален для быстрого развертывания и использования сервиса без необходимости работать с исходным кодом.

#### Шаг 1: Создайте папку для проекта и файлы конфигурации
Создайте пустую папку, где будут храниться ваши настройки и данные.
```bash
mkdir my-telegram-parser && cd my-telegram-parser
```

#### Шаг 2: Создайте файл `docker-compose.yml`
Создайте в этой папке файл `docker-compose.yml` и вставьте в него следующее содержимое. Этот файл настроен на использование готового образа из Docker Hub.

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:13
    volumes: ["postgres_data:/var/lib/postgresql/data/"]
    environment: ["POSTGRES_USER=${POSTGRES_USER}","POSTGRES_PASSWORD=${POSTGRES_PASSWORD}","POSTGRES_DB=${POSTGRES_DB}"]
    ports: ["5432:5432"]
  redis:
    image: redis:6.2-alpine
    ports: ["6379:6379"]
  app:
    image: whn0thacked/telegram-api-parser:latest
    command: daphne -b 0.0.0.0 -p 8000 project.asgi:application
    volumes: ["telegram_session:/app/session/"]
    ports: ["8000:8000"]
    env_file: [".env"]
    depends_on: ["db", "redis"]
  worker:
    image: whn0thacked/telegram-api-parser:latest
    command: celery -A project.celery_app worker -l info
    volumes: ["telegram_session:/app/session/"]
    env_file: [".env"]
    depends_on: ["redis", "db"]
volumes:
  postgres_data:
  telegram_session:
```

#### Шаг 3: Создайте файл `.env`
Рядом создайте файл `.env`. **Обязательно** заполните `SECRET_KEY`, `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`.
Уникальный `SECRET_KEY` можно сгенерировать, например, [здесь](https://djecrety.ir/).

```ini
# .env
# Django Settings
SECRET_KEY=ВАШ_СЕКРЕТНЫЙ_КЛЮЧ_DJANGO
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Settings
POSTGRES_DB=telegram_parser_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# Redis
REDIS_URL=redis://redis:6379/0

# Telegram API Credentials (https://my.telegram.org)
TELEGRAM_API_ID=ВАШ_API_ID
TELEGRAM_API_HASH=ВАШ_API_HASH
TELEGRAM_SESSION_FILE=/app/session/telegram_session
TELEGRAM_SYSTEM_VERSION=4.16.30-vxCUSTOM
```

#### Шаг 4: Создайте сессию Telegram
Эта команда скачает образ и запустит интерактивный процесс авторизации. **Выполняется один раз.**
```bash
docker compose run --rm -it app python manage.py createsession
```
Введите номер телефона, код из Telegram и пароль 2FA (если есть).

#### Шаг 5: Запустите сервисы
```bash
docker compose up -d
```

#### Шаг 6: Примените миграции
```bash
docker compose exec app python manage.py migrate
```
🎉 **Готово!** Сервис работает и доступен по адресу `http://localhost:8000`.

---

### Способ 2: Установка для разработки (сборка из исходников)

Этот способ предназначен для разработчиков, которые хотят вносить изменения в исходный код.

#### Шаг 1: Клонируйте репозиторий
```bash
git clone https://github.com/your-username/Telegram-API-Parser.git
cd Telegram-API-Parser
```

#### Шаг 2: Настройте окружение
Скопируйте пример файла и заполните его своими данными (`SECRET_KEY`, `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`).
```bash
cp .env.example .env
```

#### Шаг 3: Создайте сессию Telegram
Команда автоматически соберет образ и запустит процесс авторизации.
```bash
docker compose run --rm -it app python manage.py createsession
```

#### Шаг 4: Соберите и запустите сервисы
Файл `docker-compose.yml` в репозитории уже настроен на сборку.
```bash
docker compose up --build -d
```

#### Шаг 5: Примените миграции
```bash
docker compose exec app python manage.py migrate
```
🎉 **Готово!** Теперь вы можете изменять код, и изменения будут сразу применяться внутри контейнера.

---

## 📖 Использование API

### 1. Запуск анализа канала

Отправьте `POST` запрос для создания новой задачи анализа. Задача будет добавлена в очередь и обработана фоновым воркером.

*   **URL:** `http://localhost:8000/api/analyzer/analyze/`
*   **Метод:** `POST`
*   **Тело запроса (JSON):**

    ```json
    {
        "channel_username": "durov",
        "days_to_analyze": 30,
        "price": 50000.0
    }
    ```
    *   `channel_username` (string, required): Юзернейм канала (без `@`).
    *   `days_to_analyze` (integer, optional, default: 30): Количество последних дней для анализа.
    *   `price` (float, optional, default: 1000.0): Стоимость поста для расчета CPV и CPM.

*   **Успешный ответ (202 Accepted):**
    Сервер немедленно вернет ID созданной задачи.
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    }
    ```

### 2. Проверка статуса и получение результата

Используйте `task_id`, полученный на предыдущем шаге, чтобы отслеживать статус задачи и получить результат.

*   **URL:** `http://localhost:8000/api/analyzer/tasks/{task_id}/`
*   **Метод:** `GET`

*   **Пример ответа (задача в процессе):**
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "PROGRESS",
        "channel_username": "durov",
        "days_to_analyze": 30,
        "price": 50000.0,
        "result": null,
        "error_message": null,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:01:00Z"
    }
    ```

*   **Пример ответа (успешное завершение):**
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "SUCCESS",
        "result": {
            "channel_info": {
                "username": "durov",
                "subscribers": 1784967,
                "posts_analyzed": 15,
                "period_days": 30,
                "price_used": 50000.0
            },
            "calculated_metrics": {
                "avg_views": 685331,
                "avg_reactions": 39501.7,
                "total_views": 10279965,
                "total_reactions": 592525,
                "er_percent": 2.21,
                "cpv": 0.07,
                "cpm": 72.96
            }
        },
        "error_message": null,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:02:15Z"
    }
    ```

## 📜 Лицензия

Этот проект распространяется под лицензией **GNU General Public License v3.0 (GPLv3)**. Подробности смотрите в файле `LICENSE`.
