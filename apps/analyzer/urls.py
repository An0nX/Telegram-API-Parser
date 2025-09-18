# apps/analyzer/urls.py

from django.urls import path
from .views import CreateAnalysisView, TaskStatusView

urlpatterns = [
    path("analyzer/analyze/", CreateAnalysisView.as_view(), name="create-analysis"),
    path("analyzer/tasks/<str:task_id>/", TaskStatusView.as_view(), name="task-status"),
]
