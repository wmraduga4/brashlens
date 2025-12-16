"""Telegram bot handlers."""
# Test auto-deploy
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


async def check_access_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Middleware для проверки доступа пользователя к тестовому боту.
    
    ВАЖНО: Проверка доступа выполняется ТОЛЬКО для тестового бота (IS_TEST_BOT=True).
    Для продакшн бота (IS_TEST_BOT=False) проверка не выполняется, обработка продолжается.
    
    Проверяет доступ ПЕРЕД обработкой любого сообщения.
    Если доступ запрещен - отправляет сообщение и останавливает обработку.
    Если доступ разрешен - пропускает дальше (ничего не делает).
    
    Этот обработчик должен быть добавлен ПЕРВЫМ в цепочку обработчиков (group=0).
    """
    # КРИТИЧЕСКИ ВАЖНО: Проверка доступа ТОЛЬКО для тестового бота!
    # Для продакшн бота - пропускаем без проверки
    if not settings.IS_TEST_BOT:
        # Продакшн бот - не проверяем доступ, пропускаем дальше
        context.user_data.pop('_access_denied', None)
        return
    
    user = update.effective_user
    
    if not user:
        # Если нет пользователя - пропускаем (может быть системное сообщение)
        return
    
    # Проверяем доступ (только для тестового бота)
    if not check_user_access(user.id):
        # Доступ запрещен - отправляем сообщение и останавливаем обработку
        await send_unauthorized_access_message(update, context)
        
        # Определяем тип сообщения для логирования
        message_type = "unknown"
        if update.message:
            if update.message.text:
                message_type = f"text: {update.message.text[:50]}"
            elif update.message.sticker:
                message_type = "sticker"
            elif update.message.photo:
                message_type = "photo"
            else:
                message_type = update.message.content_type or "message"
        elif update.callback_query:
            message_type = f"callback: {update.callback_query.data}"
        
        logger.warning(
            f"🚨 UNAUTHORIZED ACCESS ATTEMPT! User {user.id} tried to send {message_type} to test bot"
        )
        
        # Устанавливаем флаг в контексте, чтобы другие обработчики могли проверить
        context.user_data['_access_denied'] = True
        return
    
    # Доступ разрешен - очищаем флаг и пропускаем дальше
    # Обработка продолжается к следующим обработчикам для определения пользователя,
    # его регистрации, роли и т.д.
    context.user_data.pop('_access_denied', None)


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle sticker messages - log file_id for unauthorized access sticker."""
    # Проверка доступа уже выполнена в check_access_middleware (group=0)
    # Проверяем флаг доступа из контекста
    if context.user_data.get('_access_denied'):
        return
    
    user = update.effective_user
    sticker = update.message.sticker
    
    if sticker:
        logger.info(
            f"Sticker received from user {user.id}: "
            f"file_id={sticker.file_id}, "
            f"file_unique_id={sticker.file_unique_id}, "
            f"set_name={sticker.set_name}, "
            f"emoji={sticker.emoji}"
        )
        # Отправляем обратно информацию о стикере
        await update.message.reply_text(
            f"✅ Стикер получен!\n\n"
            f"**file_id:** `{sticker.file_id}`\n"
            f"**file_unique_id:** `{sticker.file_unique_id}`\n"
            f"**set_name:** `{sticker.set_name or 'N/A'}`\n"
            f"**emoji:** {sticker.emoji or 'N/A'}\n\n"
            f"Используйте этот file_id для отправки стикера в сообщении о несанкционированном доступе.",
            parse_mode="Markdown"
        )


async def send_unauthorized_access_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет сообщение о несанкционированном доступе со стикером.
    
    Args:
        update: Telegram Update объект
        context: Context объект
    """
    unauthorized_text = (
        "🚫 **СТОП! HALT! ALTO!**\n\n"
        "Обнаружена попытка несанкционированного проникновения к тестовому боту. "
        "Ты кто такой? Давай, до свидания! (шутка, дорогой, не обижайся)\n\n"
        "🔐 Доступ разрешен только для авторизованных разработчиков. "
        "Ты вроде не из наших... пока что.\n\n"
        "📝 Кстати, мы всё записали: твой ID, время визита, что пытался сделать. "
        "Не для доноса начальству, а так... чисто для логов. Так положено 🤟"
    )
    
    try:
        if update.message:
            # Отправляем текстовое сообщение о несанкционированном доступе
            # Стикер можно добавить позже, когда будет актуальный file_id
            await update.message.reply_text(
                unauthorized_text,
                parse_mode="Markdown"
            )
            logger.info(f"Sent unauthorized access message to user {update.effective_user.id}")
            
        elif update.callback_query:
            await update.callback_query.answer("🚨 НЕСАНКЦИОНИРОВАННЫЙ ДОСТУП!", show_alert=True)
            await update.callback_query.edit_message_text(
                unauthorized_text,
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error sending unauthorized access message: {e}")
        # Fallback - просто текст
        if update.message:
            await update.message.reply_text(
                "🚫 СТОП! HALT! ALTO!\n\n"
                "Обнаружена попытка несанкционированного проникновения к тестовому боту. "
                "Ты кто такой? Давай, до свидания! (шутка, дорогой, не обижайся)\n\n"
                "🔐 Доступ разрешен только для авторизованных разработчиков. "
                "Ты вроде не из наших... пока что.\n\n"
                "📝 Кстати, мы всё записали: твой ID, время визита, что пытался сделать. "
                "Не для доноса начальству, а так... чисто для логов. Так положено 🤟"
            )


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
    
    # Проверка доступа уже выполнена в check_access_middleware (group=0)
    # Проверяем флаг доступа из контекста
    if context.user_data.get('_access_denied'):
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
    
    # Проверка доступа уже выполнена в check_access_middleware (group=0)
    # Проверяем флаг доступа из контекста
    if context.user_data.get('_access_denied'):
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
    
    # Проверка доступа уже выполнена в check_access_middleware (group=0)
    # Проверяем флаг доступа из контекста
    if context.user_data.get('_access_denied'):
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
