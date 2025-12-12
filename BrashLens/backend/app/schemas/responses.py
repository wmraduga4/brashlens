"""Response schemas for API endpoints."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Ответ health check endpoint."""
    status: str = Field(..., description="Статус приложения")
    timestamp: str = Field(..., description="Временная метка в ISO формате")


class HealthDbResponse(BaseModel):
    """Ответ health check для БД."""
    status: str = Field(..., description="Статус подключения")
    database: str = Field(..., description="Статус БД")
    version: Optional[str] = Field(None, description="Версия PostgreSQL")
    error: Optional[str] = Field(None, description="Ошибка подключения")


class TestConnectionResponse(BaseModel):
    """Ответ при создании тестовой записи."""
    status: str = Field(..., description="Статус операции")
    message: str = Field(..., description="Сообщение о результате")
    id: str = Field(..., description="UUID созданной записи")
    created_at: str = Field(..., description="Время создания в ISO формате")


class TestConnectionRecord(BaseModel):
    """Модель тестовой записи."""
    id: str = Field(..., description="UUID записи")
    message: str = Field(..., description="Сообщение")
    created_at: str = Field(..., description="Время создания в ISO формате")


class TestConnectionsListResponse(BaseModel):
    """Ответ со списком тестовых записей."""
    status: str = Field(..., description="Статус операции")
    count: int = Field(..., description="Количество записей")
    records: list[TestConnectionRecord] = Field(..., description="Список записей")


class RedisTestResponse(BaseModel):
    """Ответ проверки подключения к Redis."""
    redis: str = Field(..., description="Статус Redis (ok/error)")


class CacheSetResponse(BaseModel):
    """Ответ при сохранении в кеш."""
    status: str = Field(..., description="Статус операции")


class CacheGetResponse(BaseModel):
    """Ответ при получении из кеша."""
    key: str = Field(..., description="Ключ")
    value: str = Field(..., description="Значение")


class CeleryTaskResponse(BaseModel):
    """Ответ при запуске Celery задачи."""
    task_id: str = Field(..., description="ID задачи")


class TaskStatusResponse(BaseModel):
    """Ответ со статусом Celery задачи."""
    status: str = Field(..., description="Статус задачи (PENDING/SUCCESS/FAILURE)")
    task_id: str = Field(..., description="ID задачи")
    result: Optional[dict] = Field(None, description="Результат выполнения")
    error: Optional[str] = Field(None, description="Ошибка выполнения")
