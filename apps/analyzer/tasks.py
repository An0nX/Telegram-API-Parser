# apps/analyzer/tasks.py

from project.celery_app import app as celery_app
from .models import AnalysisTask
from .services import TelegramService
from .formulas import calculate_channel_metrics


@celery_app.task(
    bind=True,
    autoretry_for=(AnalysisTask.DoesNotExist,),
    retry_kwargs={"max_retries": 5, "countdown": 3},
)
def analyze_channel_task(self, task_db_id: int):
    """
    Полностью синхронная Celery-задача для анализа постов Telegram-канала.
    """
    try:
        task_instance = AnalysisTask.objects.get(id=task_db_id)
    except AnalysisTask.DoesNotExist as exc:
        raise exc

    task_instance.status = AnalysisTask.Status.PROGRESS
    task_instance.save(update_fields=["status"])

    self.update_state(
        state="PROGRESS",
        meta={"status": "Запуск анализа", "channel": task_instance.channel_username},
    )

    try:
        tg_service = TelegramService()
        raw_data = tg_service.analyze_channel_posts(
            task_instance.channel_username, task_instance.days_to_analyze
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Расчет метрик",
                "posts_found": raw_data["posts_analyzed_count"],
            },
        )

        metrics = calculate_channel_metrics(
            raw_data["posts_data"],
            raw_data["subscribers_count"],
            task_instance.price,  # Передаем цену в калькулятор
        )

        result = {
            "channel_info": {
                "username": task_instance.channel_username,
                "subscribers": raw_data["subscribers_count"],
                "posts_analyzed": raw_data["posts_analyzed_count"],
                "period_days": task_instance.days_to_analyze,
                "price_used": task_instance.price,
            },
            "calculated_metrics": metrics,
        }

        task_instance.result = result
        task_instance.status = AnalysisTask.Status.SUCCESS
        task_instance.save(update_fields=["result", "status"])
        return result

    except Exception as e:
        task_instance.status = AnalysisTask.Status.FAILURE
        task_instance.error_message = str(e)
        task_instance.save(update_fields=["status", "error_message"])
        raise e
