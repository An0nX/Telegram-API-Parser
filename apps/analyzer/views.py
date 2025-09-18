# apps/analyzer/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from .models import AnalysisTask
from .serializers import AnalysisTaskSerializer, CreateChannelAnalysisSerializer
from .tasks import analyze_channel_task


class CreateAnalysisView(generics.CreateAPIView):
    """
    API-эндпоинт для создания и запуска задачи анализа канала.
    """

    serializer_class = CreateChannelAnalysisSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_instance = AnalysisTask.objects.create(**serializer.validated_data)

        task_result = analyze_channel_task.delay(task_db_id=task_instance.id)

        task_instance.task_id = task_result.id
        task_instance.save(update_fields=["task_id"])

        return Response(
            {"task_id": task_instance.task_id}, status=status.HTTP_202_ACCEPTED
        )


class TaskStatusView(generics.RetrieveAPIView):
    """
    API-эндпоинт для получения статуса и результата задачи по её ID.
    """

    queryset = AnalysisTask.objects.all()
    serializer_class = AnalysisTaskSerializer
    lookup_field = "task_id"
