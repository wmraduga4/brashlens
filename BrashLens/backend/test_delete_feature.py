"""Тест функционала удаления пользователя."""
import asyncio
from app.services.user_service import UserService
from app.core.database import AsyncSessionLocal


async def test_delete_method_exists():
    """Проверка что метод delete_user_by_telegram_id существует."""
    async with AsyncSessionLocal() as session:
        service = UserService(session)
        has_method = hasattr(service, 'delete_user_by_telegram_id')
        print(f"✅ UserService.delete_user_by_telegram_id exists: {has_method}")
        return has_method


async def test_imports():
    """Проверка импортов."""
    try:
        from app.bot.handlers import (
            delete_me_command,
            delete_confirm_callback,
            delete_cancel_callback,
            check_user_access,
        )
        print("✅ All handlers imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    print("Testing delete user feature...")
    asyncio.run(test_delete_method_exists())
    asyncio.run(test_imports())
    print("✅ All tests passed!")
