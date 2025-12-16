"""Сервис для работы с пользователями."""
from typing import List, Optional
import logging

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя."""
        # Проверка существования по telegram_id
        existing = await self.get_by_telegram_id(user_data.telegram_id)
        if existing:
            raise ValueError(
                f"User with telegram_id {user_data.telegram_id} already exists"
            )

        # Создание пользователя
        user_dict = user_data.model_dump()
        # Конвертируем строку роли в enum
        if "role" in user_dict and isinstance(user_dict["role"], str):
            user_dict["role"] = UserRole(user_dict["role"])
        user = User(**user_dict)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID."""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def update_user(
        self, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """Обновить данные пользователя."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Обновляем только переданные поля
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_users_by_role(
        self, role: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Получить список пользователей по роли."""
        # Конвертируем строку в enum если нужно
        role_enum = UserRole(role) if isinstance(role, str) else role
        result = await self.db.execute(
            select(User)
            .where(and_(User.role == role_enum, User.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def deactivate_user(self, user_id: int) -> bool:
        """Деактивировать пользователя (soft delete)."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        await self.db.commit()
        return True

    async def get_or_create_user(
        self, telegram_id: int, user_data: UserCreate
    ) -> tuple[User, bool]:
        """
        Получить существующего пользователя или создать нового.

        Returns:
            tuple[User, bool]: (user, created) где created=True если пользователь создан
        """
        existing = await self.get_by_telegram_id(telegram_id)
        if existing:
            return existing, False

        user = await self.create_user(user_data)
        return user, True

    async def delete_user_by_telegram_id(self, telegram_id: int) -> bool:
        """
        Полное удаление пользователя и всех связанных данных.
        
        Best practices:
        - Использует транзакцию для атомарности
        - Явное удаление связанных данных (контроль)
        - Логирование каждого шага
        - Rollback при ошибке
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            bool: True если удаление успешно, False если пользователь не найден
            
        Raises:
            Exception: При ошибке БД (транзакция откатывается)
        """
        try:
            # Находим пользователя
            user = await self.get_by_telegram_id(telegram_id)
            if not user:
                logger.warning(f"User with telegram_id {telegram_id} not found for deletion")
                return False
            
            user_id = user.id
            username = user.username or f"user_{user_id}"
            
            logger.info(
                f"Starting deletion of user {user_id} "
                f"(telegram_id: {telegram_id}, username: {username})"
            )
            
            # Проверяем наличие Photographer (если модель существует)
            # Используем try/except для безопасной проверки
            photographer = None
            photographer_settings = None
            
            try:
                from app.models.photographer import Photographer, PhotographerSettings
                
                photographer_result = await self.db.execute(
                    select(Photographer).where(Photographer.user_id == user_id)
                )
                photographer = photographer_result.scalar_one_or_none()
                
                if photographer:
                    photographer_id = photographer.id
                    logger.info(
                        f"Found Photographer profile {photographer_id}, "
                        f"deleting related data..."
                    )
                    
                    # Удаляем PhotographerSettings
                    await self.db.execute(
                        delete(PhotographerSettings).where(
                            PhotographerSettings.photographer_id == photographer_id
                        )
                    )
                    logger.info(
                        f"Deleted PhotographerSettings for photographer {photographer_id}"
                    )
                    
                    # Удаляем Photographer
                    await self.db.execute(
                        delete(Photographer).where(Photographer.id == photographer_id)
                    )
                    logger.info(f"Deleted Photographer {photographer_id}")
            except ImportError:
                # Модель Photographer еще не создана - это нормально
                logger.debug("Photographer model not found, skipping related data deletion")
            except Exception as e:
                logger.warning(f"Error checking/deleting Photographer: {e}")
            
            # Удаляем User
            await self.db.execute(
                delete(User).where(User.id == user_id)
            )
            logger.info(f"Deleted User {user_id}")
            
            # Commit всей транзакции
            await self.db.commit()
            
            removed_items = "User"
            if photographer:
                removed_items += ", Photographer, PhotographerSettings"
            
            logger.info(
                f"Successfully deleted user {user_id} "
                f"(telegram_id: {telegram_id}, username: {username}). "
                f"Removed: {removed_items}"
            )
            
            return True
            
        except Exception as e:
            # Rollback при любой ошибке
            await self.db.rollback()
            logger.error(
                f"Error deleting user {telegram_id}: {e}",
                exc_info=True
            )
            raise  # Пробрасываем дальше для обработки в handler
