"""API v1 routes."""
from fastapi import APIRouter

from app.api.v1 import health, test, cache, tasks, users

# Создаем главный роутер для v1
api_router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    responses={
        404: {"description": "Not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)

# Подключаем подроутеры
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(users.router)
# Webhook обрабатывается отдельным микросервисом бота через его собственный веб-сервер (порт 8443)
