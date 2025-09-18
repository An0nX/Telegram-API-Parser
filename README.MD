### 1. Конфигурация

Перед первым запуском необходимо настроить переменные окружения.

1.  **Скопируйте файл с примером:**
    ```bash
    cp .env.example .env
    ```

2.  **Отредактируйте файл `.env`:**
    Откройте файл `.env` в текстовом редакторе и заполните следующие значения:

    *   `SECRET_KEY`: Сгенерируйте уникальный ключ для Django.
    *   `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`: Получите эти значения на сайте [my.telegram.org](https://my.telegram.org).

### 2. Создание сессии Telegram (Обязательный первый шаг!)

Для работы сервиса требуется авторизованная сессия Telegram. Для этого была создана специальная Django-команда. **Эту процедуру нужно выполнить только один раз.**

1.  **Запустите команду `createsession` в интерактивном режиме:**
    Выполните в терминале следующую команду. Флаг `-it` критически важен, так как он позволяет вводить данные в консоль.
    ```bash
    docker compose run --rm -it app python manage.py createsession
    ```

2.  **Следуйте инструкциям в консоли:**
    *   Скрипт попросит вас ввести номер телефона, к которому привязан Telegram-аккаунт.
    *   Затем он запросит код подтверждения, который придет вам в Telegram.
    *   Если у вас включена двухфакторная аутентификация (облачный пароль), скрипт также попросит ввести его.

    После успешного входа сессия будет сохранена, и вы сможете запускать проект.

### 3. Запуск проекта

После успешного создания сессии можно запускать все сервисы.

1.  **Сборка и запуск контейнеров в фоновом режиме:**
    ```bash
    docker compose up --build -d
    ```

2.  **Применение миграций базы данных:**
    (Этот шаг нужно выполнить после предыдущих изменений в модели)
    ```bash
    docker compose exec app python manage.py makemigrations analyzer
    docker compose exec app python manage.py migrate
    ```

3.  **Сбор статических файлов:**
    ```bash
    docker compose exec app python manage.py collectstatic --no-input
    ```

4.  **(Опционально) Создание суперпользователя для админ-панели:**
    ```bash
    docker compose exec app python manage.py createsuperuser
    ```

Проект запущен и готов к работе!

---

## Использование API

Сервис доступен по адресу `http://localhost:8000`.

### 1. Запуск анализа канала

Отправьте `POST` запрос на эндпоинт для создания новой задачи анализа.

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
    *   `channel_username`: Юзернейм канала (без `@`).
    *   `days_to_analyze`: Количество последних дней для анализа (по умолчанию 30).
    *   `price`: Цена для расчетов. **(Опционально, по умолчанию 1000.0)**.

*   **Успешный ответ (202 Accepted):**
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    }
    ```

### 2. Проверка статуса и получение результата

*   **URL:** `http://localhost:8000/api/analyzer/tasks/{task_id}/`
*   **Метод:** `GET`

*   **Пример ответа (успех):**
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "SUCCESS",
        // ...
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
                "cpv": 72.96,
                "cpm": 72960.33
            }
        }
    }
    ```

---

## Полезные команды Docker Compose

*   **Остановить все сервисы:**
    ```bash
    docker compose down
    ```
*   **Остановить и удалить volumes:**
    ```bash
    docker compose down -v
    ```
*   **Просмотр логов:**
    ```bash
    docker compose logs -f worker
    ```