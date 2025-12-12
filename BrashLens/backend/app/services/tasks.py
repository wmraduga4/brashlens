"""Celery tasks."""
import logging
import time

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.services.tasks.test_task")
def test_task(message: str) -> dict[str, str]:
    """
    Тестовая задача для проверки работы Celery.
    
    Args:
        message: Сообщение для логирования
        
    Returns:
        dict: Результат выполнения задачи
    """
    logger.info(f"Test task started with message: {message}")
    
    # Имитация работы (5 секунд)
    time.sleep(5)
    
    result = {
        "status": "completed",
        "message": message,
    }
    
    logger.info(f"Test task completed: {result}")
    return result


@celery_app.task(name="app.services.tasks.add_numbers")
def add_numbers(a: int, b: int) -> dict[str, int]:
    """
    Простая задача для сложения чисел.
    
    Args:
        a: Первое число
        b: Второе число
        
    Returns:
        dict: Результат сложения
    """
    logger.info(f"Adding numbers: {a} + {b}")
    result = a + b
    logger.info(f"Result: {result}")
    return {"result": result}
