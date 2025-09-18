# apps/analyzer/management/commands/createsession.py

from getpass import getpass
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError


class Command(BaseCommand):
    """
    Django-команда для интерактивного создания и авторизации сессии Telethon.
    """

    help = "Creates and authorizes a new Telethon session file."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Запуск создания сессии Telegram ---"))
        self.stdout.write(
            "Сессионный файл будет сохранен в: " + settings.TELEGRAM_SESSION_FILE
        )

        client = TelegramClient(
            settings.TELEGRAM_SESSION_FILE,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
            system_version=settings.TELEGRAM_SYSTEM_VERSION,
        )

        try:
            client.connect()
            if client.is_user_authorized():
                self.stdout.write(
                    self.style.SUCCESS(
                        "Сессия уже авторизована. Ничего делать не нужно."
                    )
                )
                client.disconnect()
                return

            phone = input("Пожалуйста, введите ваш номер телефона (в формате +7...): ")
            code_hash = client.send_code_request(phone).phone_code_hash
            client.sign_in(
                phone,
                input("Пожалуйста, введите код подтверждения: "),
                phone_code_hash=code_hash,
            )

        except SessionPasswordNeededError:
            password = getpass(
                "Включена 2FA. Пожалуйста, введите ваш облачный пароль: "
            )
            client.sign_in(password=password)

        except PhoneCodeInvalidError:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Неверный код. Пожалуйста, запустите команду снова."
                )
            )
            client.disconnect()
            return

        except EOFError:
            raise CommandError(
                "\nНе удалось прочитать ввод. Пожалуйста, запустите команду в интерактивном режиме, "
                "используя флаг '-it':\n"
                "docker compose run --rm -it app python manage.py createsession"
            )

        except KeyboardInterrupt:
            self.stdout.write("\nПроцесс прерван пользователем.")
            client.disconnect()
            return

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Произошла непредвиденная ошибка: {e}")
            )
            client.disconnect()
            return

        me = client.get_me()
        self.stdout.write("-" * 30)
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Успешный вход как: {me.first_name} (@{me.username})"
            )
        )
        self.stdout.write(self.style.SUCCESS("✅ Сессия успешно сохранена."))
        self.stdout.write("-" * 30)

        client.disconnect()
