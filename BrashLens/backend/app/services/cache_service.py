"""Cache service for Redis operations."""
import logging
from typing import Optional

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CacheService:
    """Сервис для работы с Redis кешем."""

    def __init__(self, redis_client: Redis):
        """
        Инициализация CacheService.
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

    async def ping(self) -> bool:
        """
        Проверка подключения к Redis.
        
        Returns:
            bool: True если подключение успешно, False иначе
        """
        try:
            result = await self.redis.ping()
            return result is True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """
        Сохранить значение в Redis.
        
        Args:
            key: Ключ
            value: Значение
            expire: Время жизни в секундах (по умолчанию 3600)
            
        Returns:
            bool: True если успешно сохранено
        """
        try:
            await self.redis.set(key, value, ex=expire)
            logger.info(f"Cache set: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """
        Получить значение из Redis.
        
        Args:
            key: Ключ
            
        Returns:
            Optional[str]: Значение или None если ключ не найден
        """
        try:
            value = await self.redis.get(key)
            if value:
                logger.info(f"Cache get: {key} = {value}")
            return value
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Удалить ключ из Redis.
        
        Args:
            key: Ключ для удаления
            
        Returns:
            bool: True если ключ удален
        """
        try:
            result = await self.redis.delete(key)
            logger.info(f"Cache delete: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
