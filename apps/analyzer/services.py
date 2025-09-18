# apps/analyzer/services.py

from datetime import datetime, timedelta, timezone
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors.rpcerrorlist import ChannelPrivateError, UsernameNotOccupiedError
from django.conf import settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class TelegramService:
    """
    Полностью синхронная версия сервиса для работы с Telethon.
    Использует 'with' для управления соединением и GetFullChannelRequest для надежного
    получения данных о канале.
    """

    def __init__(self):
        self.client = TelegramClient(
            session=settings.TELEGRAM_SESSION_FILE,
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
            system_version=settings.TELEGRAM_SYSTEM_VERSION,
            timeout=60,
        )

    def analyze_channel_posts(self, channel_username: str, days: int):
        """
        Собирает статистику по всем постам канала в синхронном режиме.
        """
        logger.info(f"Начинаем анализ канала {channel_username}...")

        with self.client:
            logger.info(
                "Клиент подключен и авторизован. Получаем информацию о канале..."
            )

            try:
                channel = self.client.get_entity(channel_username)
            except (
                ChannelPrivateError,
                UsernameNotOccupiedError,
                ValueError,
                TypeError,
            ):
                logger.error(
                    f"Канал '{channel_username}' не найден или является приватным."
                )
                raise ValueError(
                    f"Канал '{channel_username}' не найден или является приватным."
                )

            # Правильный способ получения количества подписчиков.
            # GetFullChannelRequest возвращает полную информацию о канале.
            try:
                full_channel_info = self.client(GetFullChannelRequest(channel=channel))
                subscribers_count = full_channel_info.full_chat.participants_count
            except Exception as e:
                logger.warning(
                    f"Не удалось получить полную информацию о канале {channel_username}. "
                    f"Количество подписчиков будет равно 0. Ошибка: {e}"
                )
                subscribers_count = 0

            posts_data = []

            logger.info(f"Начинаем итерацию постов за последние {days} дней...")
            offset_date = datetime.now(timezone.utc) - timedelta(days=days)
            posts_processed = 0

            # Итерация по сообщениям, ограниченная датой.
            for message in self.client.iter_messages(
                channel, offset_date=datetime.now(timezone.utc)
            ):
                if not message.date or message.date < offset_date:
                    break

                if not message.views:
                    continue

                reactions_count = 0
                if message.reactions:
                    reactions_count = sum(r.count for r in message.reactions.results)

                posts_data.append(
                    {"views": message.views, "reactions": reactions_count}
                )
                posts_processed += 1

                if posts_processed % 50 == 0:  # Увеличил шаг для логов
                    logger.info(f"Обработано {posts_processed} постов...")

            logger.info(f"Сбор завершен. Проанализировано {posts_processed} постов.")

            return {
                "subscribers_count": subscribers_count,
                "posts_data": posts_data,
                "posts_analyzed_count": posts_processed,
            }
