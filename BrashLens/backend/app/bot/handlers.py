"""Telegram bot handlers."""
# Test auto-deploy
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


def check_user_access(telegram_id: int) -> bool:
    """
    Проверка доступа пользователя к боту.
    
    Логика:
    - Если IS_TEST_BOT=False или None (продакшн бот) - доступ для всех
    - Если IS_TEST_BOT=True (тестовый бот):
      - Если TEST_BOT_ALLOWED_USER_ID не установлен - доступ для всех
      - Если TEST_BOT_ALLOWED_USER_ID установлен - только этот пользователь
    
    Args:
        telegram_id: Telegram ID пользователя
        
    Returns:
        bool: True если доступ разрешен, False если запрещен
    """
    # Продакшн бот - доступ для всех (IS_TEST_BOT может быть None, False или не установлен)
    if not settings.IS_TEST_BOT:
        return True
    
    # Тестовый бот - проверяем доступ
    if settings.TEST_BOT_ALLOWED_USER_ID is None:
        # Проверка отключена - доступ для всех
        logger.debug(f"Test bot: access allowed for all (TEST_BOT_ALLOWED_USER_ID not set)")
        return True
    
    if telegram_id == settings.TEST_BOT_ALLOWED_USER_ID:
        logger.debug(f"Test bot: access allowed for user {telegram_id}")
        return True
    
    logger.warning(
        f"Test bot: access denied for user {telegram_id}. "
        f"Allowed user: {settings.TEST_BOT_ALLOWED_USER_ID}"
    )
    return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    
    # Проверка доступа для тестового бота
    if not check_user_access(user.id):
        await update.message.reply_text(
            "🚨 **АТУНГ! ПОПЫТКА НЕСАНКЦИОНИРОВАННОГО ВТОРЖЕНИЯ!!!** 🚨\n\n"
            "⚠️ Обнаружена попытка несанкционированного доступа к тестовому боту.\n\n"
            "🔒 Доступ разрешен только для авторизованных пользователей.\n\n"
            "📋 Все попытки доступа логируются и отслеживаются.",
            parse_mode="Markdown"
        )
        logger.warning(f"🚨 UNAUTHORIZED ACCESS ATTEMPT! User {user.id} tried to access test bot in /start command")
        return
    
    # Проверяем существование пользователя
    async with AsyncSessionLocal() as session:
        service = UserService(session)
        existing_user = await service.get_by_telegram_id(user.id)
    
    if existing_user:
        # Пользователь зарегистрирован - показываем меню с кнопкой удаления
        role_text = {
            "photographer": "📸 Вы зарегистрированы как фотограф.",
            "client": "👤 Вы зарегистрированы как клиент."
        }
        
        text = (
            f"👋 Привет, {existing_user.first_name}!\n\n"
            f"{role_text.get(existing_user.role.value, '')}\n\n"
            "Используйте /start для обновления или /help для списка команд."
        )
        
        # Кнопки для зарегистрированных
        keyboard = [
            [
                InlineKeyboardButton(
                    "🗑️ Удали меня",
                    callback_data="delete_me"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup
        )
    else:
        # Новый пользователь - выбор роли
        keyboard = [
            [
                InlineKeyboardButton("📸 Я фотограф", callback_data="role_photographer"),
                InlineKeyboardButton("👤 Я клиент", callback_data="role_client"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Привет! Я BrashLens бот. 🤝\n\n"
            "Выберите вашу роль:",
            reply_markup=reply_markup
        )
    
    logger.info(f"User {user.id} sent /start command")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline buttons."""
    query = update.callback_query
    user = update.effective_user
    
    # Проверка доступа для тестового бота
    if not check_user_access(user.id):
        await query.answer("🚨 НЕСАНКЦИОНИРОВАННЫЙ ДОСТУП!", show_alert=True)
        await query.edit_message_text(
            "🚨 **АТУНГ! ПОПЫТКА НЕСАНКЦИОНИРОВАННОГО ВТОРЖЕНИЯ!!!** 🚨\n\n"
            "⚠️ Обнаружена попытка несанкционированного доступа к тестовому боту.\n\n"
            "🔒 Доступ разрешен только для авторизованных пользователей.\n\n"
            "📋 Все попытки доступа логируются и отслеживаются.",
            parse_mode="Markdown"
        )
        logger.warning(f"🚨 UNAUTHORIZED ACCESS ATTEMPT! User {user.id} tried to access test bot in callback")
        return
    
    await query.answer()
    
    if query.data == "role_photographer":
        await query.edit_message_text("📸 Отлично! Вы выбрали роль фотографа.")
        logger.info(f"User {user.id} selected photographer role")
    elif query.data == "role_client":
        await query.edit_message_text("👤 Отлично! Вы выбрали роль клиента.")
        logger.info(f"User {user.id} selected client role")
    elif query.data == "delete_me":
        # Показываем подтверждение удаления
        await delete_me_command_from_callback(update, context)
    elif query.data == "delete_confirm":
        await delete_confirm_callback(update, context)
    elif query.data == "delete_cancel":
        await delete_cancel_callback(update, context)
    else:
        await query.edit_message_text("Неизвестная команда.")


async def delete_me_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Команда /delete_me - показывает подтверждение удаления.
    
    Best practices:
    - Показывает предупреждение
    - Требует явного подтверждения
    - Использует inline кнопки для UX
    """
    user = update.effective_user
    
    # Проверка доступа
    if not check_user_access(user.id):
        await update.message.reply_text(
            "🚨 **АТУНГ! ПОПЫТКА НЕСАНКЦИОНИРОВАННОГО ВТОРЖЕНИЯ!!!** 🚨\n\n"
            "⚠️ Обнаружена попытка несанкционированного доступа к тестовому боту.\n\n"
            "🔒 Доступ разрешен только для авторизованных пользователей.\n\n"
            "📋 Все попытки доступа логируются и отслеживаются.",
            parse_mode="Markdown"
        )
        logger.warning(f"🚨 UNAUTHORIZED ACCESS ATTEMPT! User {user.id} tried to use /delete_me command")
        return
    
    # Проверяем что пользователь существует
    async with AsyncSessionLocal() as session:
        service = UserService(session)
        existing_user = await service.get_by_telegram_id(user.id)
        
        if not existing_user:
            await update.message.reply_text(
                "❌ Аккаунт не найден. Возможно, уже удален.\n\n"
                "Используйте /start для регистрации."
            )
            return
    
    # Показываем предупреждение с подтверждением
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Да, удалить навсегда",
                callback_data="delete_confirm"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Отмена",
                callback_data="delete_cancel"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    warning_text = (
        "⚠️ **ВНИМАНИЕ! Это действие нельзя отменить.**\n\n"
        "Вы действительно хотите удалить свой аккаунт?\n\n"
        "**Будет удалено:**\n"
        "• Все ваши данные\n"
        "• Профиль фотографа (если есть)\n"
        "• Настройки и портфолио\n"
        "• Все связанные данные\n\n"
        "**Это действие необратимо!**\n\n"
        "После удаления вы сможете зарегистрироваться заново через /start."
    )
    
    await update.message.reply_text(
        warning_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    logger.info(f"User {user.id} requested account deletion confirmation")


async def delete_me_command_from_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Показывает подтверждение удаления из callback (для кнопки в меню)."""
    query = update.callback_query
    user = update.effective_user
    
    # Проверяем что пользователь существует
    async with AsyncSessionLocal() as session:
        service = UserService(session)
        existing_user = await service.get_by_telegram_id(user.id)
        
        if not existing_user:
            await query.answer("Аккаунт не найден", show_alert=True)
            await query.edit_message_text(
                "❌ Аккаунт не найден. Возможно, уже удален.\n\n"
                "Используйте /start для регистрации."
            )
            return
    
    # Показываем предупреждение с подтверждением
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Да, удалить навсегда",
                callback_data="delete_confirm"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Отмена",
                callback_data="delete_cancel"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    warning_text = (
        "⚠️ **ВНИМАНИЕ! Это действие нельзя отменить.**\n\n"
        "Вы действительно хотите удалить свой аккаунт?\n\n"
        "**Будет удалено:**\n"
        "• Все ваши данные\n"
        "• Профиль фотографа (если есть)\n"
        "• Настройки и портфолио\n"
        "• Все связанные данные\n\n"
        "**Это действие необратимо!**\n\n"
        "После удаления вы сможете зарегистрироваться заново через /start."
    )
    
    await query.edit_message_text(
        warning_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    logger.info(f"User {user.id} requested account deletion confirmation (from button)")


async def delete_confirm_callback(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Подтверждение удаления - выполняет удаление.
    
    Best practices:
    - Обрабатывает ошибки gracefully
    - Показывает понятные сообщения
    - Логирует результат
    """
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    telegram_id = user.id
    
    try:
        async with AsyncSessionLocal() as session:
            service = UserService(session)
            deleted = await service.delete_user_by_telegram_id(telegram_id)
            
            if deleted:
                success_text = (
                    "✅ **Аккаунт успешно удален!**\n\n"
                    "Все ваши данные удалены из системы.\n\n"
                    "Для новой регистрации используйте команду:\n"
                    "`/start`\n\n"
                    "Спасибо за использование BrashLens! 👋"
                )
                
                await query.edit_message_text(
                    success_text,
                    parse_mode="Markdown"
                )
                logger.info(f"User {telegram_id} successfully deleted their account")
            else:
                await query.edit_message_text(
                    "❌ Аккаунт не найден. Возможно, уже удален.\n\n"
                    "Используйте /start для регистрации."
                )
                
    except Exception as e:
        logger.error(
            f"Error deleting user {telegram_id}: {e}",
            exc_info=True
        )
        await query.edit_message_text(
            "❌ Произошла ошибка при удалении аккаунта.\n\n"
            "Попробуйте позже или обратитесь в поддержку.\n\n"
            "Ошибка зафиксирована в логах."
        )


async def delete_cancel_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Отмена удаления."""
    query = update.callback_query
    await query.answer("Удаление отменено")
    
    await query.edit_message_text(
        "✅ Удаление отменено.\n\n"
        "Ваш аккаунт в безопасности."
    )
    logger.info(f"User {update.effective_user.id} cancelled account deletion")
