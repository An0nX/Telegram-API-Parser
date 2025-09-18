# apps/analyzer/models.py

from django.db import models


class AnalysisTask(models.Model):
    """
    Модель для хранения задачи анализа Telegram-канала и её результата.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "В ожидании"
        PROGRESS = "PROGRESS", "В процессе"
        SUCCESS = "SUCCESS", "Успешно"
        FAILURE = "FAILURE", "Ошибка"

    task_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID задачи Celery",
    )

    channel_username = models.CharField(max_length=100)
    days_to_analyze = models.IntegerField(default=30)
    price = models.FloatField(default=1000.0)  # Цена для расчета метрик

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    result = models.JSONField(null=True, blank=True, verbose_name="Результат анализа")
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Анализ канала {self.channel_username} за {self.days_to_analyze} дней ({self.status})"
