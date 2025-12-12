"""Redis cache endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from app.core.redis import get_redis
from app.services.cache_service import CacheService
from app.schemas.requests import CacheRequest
from app.schemas.responses import RedisTestResponse, CacheSetResponse, CacheGetResponse

router = APIRouter()


@router.get(
    "/test",
    response_model=RedisTestResponse,
    summary="Test Redis connection",
    description="Проверить подключение к Redis. Выполняет команду PING для проверки доступности.",
    responses={
        200: {
            "description": "Результат проверки подключения",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Redis доступен",
                            "value": {"redis": "ok"}
                        },
                        "error": {
                            "summary": "Redis недоступен",
                            "value": {"redis": "error"}
                        }
                    }
                }
            }
        }
    }
)
async def test_redis(redis: Redis = Depends(get_redis)) -> RedisTestResponse:
    """
    Проверить подключение к Redis.
    
    Args:
        redis: Redis client instance
        
    Returns:
        RedisTestResponse: Статус подключения к Redis
    """
    cache_service = CacheService(redis)
    is_ok = await cache_service.ping()
    
    return RedisTestResponse(redis="ok" if is_ok else "error")


@router.post(
    "",
    response_model=CacheSetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set cache value",
    description="Сохранить значение в Redis кеш с TTL по умолчанию 3600 секунд (1 час).",
    responses={
        201: {
            "description": "Значение успешно сохранено",
            "content": {
                "application/json": {
                    "example": {"status": "saved"}
                }
            }
        },
        500: {
            "description": "Ошибка при сохранении",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to save to cache"}
                }
            }
        }
    }
)
async def set_cache(
    request: CacheRequest,
    redis: Redis = Depends(get_redis)
) -> CacheSetResponse:
    """
    Сохранить значение в Redis кеш.
    
    Args:
        request: Ключ и значение для сохранения
        redis: Redis client instance
        
    Returns:
        CacheSetResponse: Статус операции
        
    Raises:
        HTTPException: При ошибке сохранения
    """
    cache_service = CacheService(redis)
    success = await cache_service.set(request.key, request.value)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save to cache"
        )
    
    return CacheSetResponse(status="saved")


@router.get(
    "/{key}",
    response_model=CacheGetResponse,
    summary="Get cache value",
    description="Получить значение из Redis кеша по ключу.",
    responses={
        200: {
            "description": "Значение найдено",
            "content": {
                "application/json": {
                    "example": {
                        "key": "my_key",
                        "value": "my_value"
                    }
                }
            }
        },
        404: {
            "description": "Ключ не найден",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Key 'my_key' not found"
                    }
                }
            }
        }
    }
)
async def get_cache(
    key: str,
    redis: Redis = Depends(get_redis)
) -> CacheGetResponse:
    """
    Получить значение из Redis кеша по ключу.
    
    Args:
        key: Ключ для получения значения
        redis: Redis client instance
        
    Returns:
        CacheGetResponse: Ключ и значение
        
    Raises:
        HTTPException: Если ключ не найден
    """
    cache_service = CacheService(redis)
    value = await cache_service.get(key)
    
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key '{key}' not found"
        )
    
    return CacheGetResponse(key=key, value=value)
