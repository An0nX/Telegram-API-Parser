# apps/analyzer/serializers.py

from rest_framework import serializers
from .models import AnalysisTask


class CreateChannelAnalysisSerializer(serializers.Serializer):
    """
    Сериализатор для валидации входных данных при создании задачи анализа канала.
    """

    channel_username = serializers.CharField(max_length=100)
    days_to_analyze = serializers.IntegerField(default=30, min_value=1, max_value=90)
    price = serializers.FloatField(required=False, default=1000.0)


class AnalysisTaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения полной информации о задаче анализа.
    """

    class Meta:
        model = AnalysisTask
        fields = [
            "task_id",
            "status",
            "channel_username",
            "days_to_analyze",
            "price",
            "result",
            "error_message",
            "created_at",
            "updated_at",
        ]
