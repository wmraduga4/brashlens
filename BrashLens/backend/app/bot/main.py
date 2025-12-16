"""Entry point for Telegram bot service."""
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes
from app.bot.config import TELEGRAM_BOT_TOKEN
from app.bot.handlers.start import start_command, role_chosen, cancel, CHOOSING_ROLE
from app.bot.handlers.help import help_command
# Импортируем функции удаления из старого файла handlers.py
# Используем импорт с указанием модуля напрямую для избежания конфликта с папкой handlers/
import sys
import importlib.util
from pathlib import Path

# Загружаем старый handlers.py напрямую
handlers_file = Path(__file__).parent / "handlers.py"
spec = importlib.util.spec_from_file_location("app.bot.handlers_old", handlers_file)
handlers_old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handlers_old)

delete_me_command = handlers_old.delete_me_command
delete_me_command_from_callback = handlers_old.delete_me_command_from_callback
delete_confirm_callback = handlers_old.delete_confirm_callback
delete_cancel_callback = handlers_old.delete_cancel_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Инициализация после запуска бота - настройка команд меню"""
    # Настраиваем команды бота для меню
    commands = [
        BotCommand("start", "Начать работу с ботом или зарегистрироваться"),
        BotCommand("help", "Показать справку по командам"),
        BotCommand("delete_me", "Удалить свой аккаунт"),
        BotCommand("cancel", "Отменить текущую операцию"),
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands menu set successfully")


def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Conversation handler для регистрации
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            CHOOSING_ROLE: [
                CallbackQueryHandler(role_chosen, pattern="^role_")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Обработчики для удаления пользователя
    async def handle_delete_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback для удаления пользователя"""
        query = update.callback_query
        if query.data == "delete_me":
            await delete_me_command_from_callback(update, context)
        elif query.data == "delete_confirm":
            await delete_confirm_callback(update, context)
        elif query.data == "delete_cancel":
            await delete_cancel_callback(update, context)
    
    callback_handler = CallbackQueryHandler(
        handle_delete_callbacks,
        pattern="^(delete_me|delete_confirm|delete_cancel)$"
    )
    
    # Добавляем handlers
    application.add_handler(registration_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("delete_me", delete_me_command))
    application.add_handler(callback_handler)
    
    # Запускаем polling (для разработки)
    # В продакшене использовать webhook
    logger.info("Starting bot in polling mode...")
    application.run_polling()


if __name__ == "__main__":
    main()
