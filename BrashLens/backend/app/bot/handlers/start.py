"""Обработчики команды /start и регистрации пользователей."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)

# States
CHOOSING_ROLE = 0


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start
    
    1. Проверяет существование пользователя по telegram_id
    2. Если существует - показывает приветствие по роли
    3. Если новый - предлагает выбрать роль
    """
    user = update.effective_user
    
    # Получаем сервис для работы с БД
    async with AsyncSessionLocal() as db:
        service = UserService(db)
        existing_user = await service.get_by_telegram_id(user.id)
    
    if existing_user:
        # Пользователь уже зарегистрирован
        if existing_user.role.value == "photographer":
            text = (
                f"С возвращением, {existing_user.first_name}! 📸\n\n"
                "Вы можете:\n"
                "• Управлять портфолио\n"
                "• Настроить календарь\n"
                "• Посмотреть брони\n"
                "• Управлять клиентами"
            )
        else:  # client
            text = (
                f"Привет, {existing_user.first_name}! 👋\n\n"
                "Вы можете:\n"
                "• Посмотреть портфолио фотографов\n"
                "• Записаться на съемку\n"
                "• Посмотреть свои брони"
            )
        
        # Добавляем кнопку удаления аккаунта
        keyboard = [
            [InlineKeyboardButton("🗑️ Удали меня", callback_data="delete_me")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
        return ConversationHandler.END
    
    # Новый пользователь - предлагаем выбрать роль
    keyboard = [
        [InlineKeyboardButton("Я фотограф 📸", callback_data="role_photographer")],
        [InlineKeyboardButton("Я клиент 🙂", callback_data="role_client")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Добро пожаловать в BrashLens - ваш помощник в организации фотосъемок.\n\n"
        "Для начала, выберите вашу роль:"
    )
    
    await update.message.reply_text(text, reply_markup=reply_markup)
    return CHOOSING_ROLE


async def role_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    role = query.data.replace("role_", "")  # photographer или client
    
    # Определяем язык из настроек Telegram
    language = user.language_code if user.language_code in ["ru", "en"] else "ru"
    
    # Создаем пользователя
    user_data = UserCreate(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=role,
        language=language
    )
    
    try:
        async with AsyncSessionLocal() as db:
            service = UserService(db)
            created_user = await service.create_user(user_data)
        
        if role == "photographer":
            text = (
                "Отлично! Вы зарегистрированы как фотограф 📸\n\n"
                "Следующие шаги:\n"
                "1. Заполните профиль (имя, город, валюта)\n"
                "2. Загрузите портфолио\n"
                "3. Настройте календарь\n"
                "4. Создайте пакеты услуг\n\n"
                "Используйте /help для списка команд"
            )
        else:  # client
            text = (
                "Отлично! Вы зарегистрированы как клиент 🙂\n\n"
                "Теперь вы можете:\n"
                "• Просматривать портфолио фотографов\n"
                "• Записываться на съемки\n"
                "• Получать уведомления\n\n"
                "Используйте /help для списка команд"
            )
        
        await query.edit_message_text(text)
        logger.info(f"User {user.id} registered as {role}")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error creating user {user.id}: {e}", exc_info=True)
        await query.edit_message_text(
            "Произошла ошибка при регистрации. Попробуйте позже или обратитесь в поддержку."
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена регистрации"""
    await update.message.reply_text(
        "Регистрация отменена. Используйте /start для повторной попытки."
    )
    return ConversationHandler.END
