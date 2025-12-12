"""Request schemas for API endpoints."""
from pydantic import BaseModel, Field


class TestConnectionRequest(BaseModel):
    """Запрос для создания тестовой записи в БД."""
    message: str = Field(..., description="Сообщение для тестовой записи", min_length=1, max_length=255)


class CacheRequest(BaseModel):
    """Запрос для сохранения значения в Redis кеш."""
    key: str = Field(..., description="Ключ для кеша", min_length=1)
    value: str = Field(..., description="Значение для сохранения")


class CeleryTaskRequest(BaseModel):
    """Запрос для запуска Celery задачи."""
    message: str = Field(..., description="Сообщение для задачи", min_length=1)
