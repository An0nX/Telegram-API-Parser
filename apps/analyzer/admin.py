# apps/analyzer/admin.py

from django.contrib import admin
from .models import AnalysisTask


@admin.register(AnalysisTask)
class AnalysisTaskAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели AnalysisTask в админ-панели Django.
    """

    list_display = (
        "channel_username",
        "days_to_analyze",
        "price",
        "status",
        "created_at",
        "task_id",
    )
    list_filter = ("status", "channel_username")
    readonly_fields = ("created_at", "updated_at", "result", "error_message", "task_id")
    search_fields = ("channel_username", "task_id")
