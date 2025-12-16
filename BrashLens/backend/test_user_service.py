"""Тестовый скрипт для проверки UserService."""
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.schemas.user import UserCreate
from app.services.user_service import UserService


async def test_create_user():
    """Тест создания пользователя через UserService."""
    # Преобразуем postgresql:// в postgresql+asyncpg:// для async драйвера
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        service = UserService(session)

        # Создаем тестового пользователя
        user_data = UserCreate(
            telegram_id=111222333,
            username="test_user_service",
            first_name="Тест",
            last_name="Тестов",
            role="photographer",
            language="ru",
        )

        try:
            user = await service.create_user(user_data)
            print(f"✅ Пользователь создан: {user.id}, {user.first_name}")

            # Проверяем что можем получить его обратно
            found = await service.get_by_telegram_id(111222333)
            if found:
                print(f"✅ Пользователь найден: {found.username}")
            else:
                print("❌ Пользователь не найден после создания")

        except ValueError as e:
            print(f"⚠️ Пользователь уже существует (это ок для повторного запуска): {e}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback

            traceback.print_exc()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_create_user())
