"""Celery application configuration."""
import logging
from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

# Создание Celery приложения
celery_app = Celery(
    "brashlens",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.tasks"],
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Явно указываем, что нужно делать повторные попытки подключения при старте
    # Это устраняет предупреждение о deprecation и гарантирует, что ошибки подключения будут логироваться
    broker_connection_retry_on_startup=True,
    # Логируем все ошибки подключения
    broker_connection_retry=True,
    broker_connection_max_retries=10,
)

# Логируем конфигурацию брокера для отладки
logger.info(f"Celery broker configured: {settings.CELERY_BROKER_URL}")
logger.info(f"Celery backend configured: {settings.CELERY_RESULT_BACKEND}")
