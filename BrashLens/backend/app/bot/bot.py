"""Telegram bot setup and configuration."""
import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from app.bot.handlers import (
    start_command,
    handle_callback,
    delete_me_command,
    handle_sticker,
    check_access_middleware,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

# Singleton для Application (используется в webhook режиме)
_bot_application: Application | None = None


def create_application() -> Application:
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Регистрация handlers
    # ВАЖНО: check_access_middleware должен быть ПЕРВЫМ (group=0) для проверки доступа
    # перед обработкой любых сообщений, включая команды
    application.add_handler(MessageHandler(filters.ALL, check_access_middleware), group=0)
    application.add_handler(CallbackQueryHandler(check_access_middleware), group=0)
    
    # Команды и обработчики (group=1) - выполняются только если доступ разрешен
    application.add_handler(CommandHandler("start", start_command), group=1)
    application.add_handler(CommandHandler("delete_me", delete_me_command), group=1)
    application.add_handler(CallbackQueryHandler(handle_callback), group=1)
    # Обработчик стикеров (для получения file_id) - только для разрешенных пользователей
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker), group=1)
    
    return application


async def get_application() -> Application:
    """
    Получить или создать и инициализировать Application instance (singleton).
    Используется для webhook режима через FastAPI.
    
    Returns:
        Application: Telegram bot application instance
    """
    global _bot_application
    if _bot_application is None:
        _bot_application = create_application()
        await _bot_application.initialize()
        await _bot_application.start()
        logger.info("Bot application initialized for webhook mode")
    
    return _bot_application


async def setup_webhook(webhook_url: str) -> None:
    """
    Setup webhook для бота и запустить webhook сервер.
    Бот работает как отдельное приложение и обрабатывает обновления через свой webhook сервер.
    """
    from telegram.error import RetryAfter, TelegramError
    
    application = create_application()
    await application.initialize()
    await application.start()
    
    try:
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook URL set to: {webhook_url}")
    except RetryAfter as e:
        # Обработка flood control - ждем указанное время и повторяем
        logger.warning(f"Flood control: retry after {e.retry_after} seconds")
        await asyncio.sleep(e.retry_after)
        try:
            await application.bot.set_webhook(webhook_url)
            logger.info(f"Webhook URL set to: {webhook_url} (after retry)")
        except TelegramError as retry_error:
            logger.error(f"Failed to set webhook after retry: {retry_error}")
            raise
    except TelegramError as e:
        logger.error(f"Failed to set webhook: {e}")
        raise
    
    # Запускаем webhook сервер для обработки обновлений
    # Бот слушает на порту 8443 внутри контейнера
    # Nginx должен проксировать /webhook на chat-bot:8443
    logger.info("Starting webhook server on port 8443...")
    
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=8443,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )
    
    logger.info("Webhook server started on 0.0.0.0:8443")
    logger.info(f"Bot is ready to receive updates via webhook: {webhook_url}")
    logger.info("Make sure Nginx proxies /webhook to chat-bot:8443")
    
    # Ждем бесконечно
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Stopping webhook server...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


async def start_polling() -> None:
    """Start bot in polling mode."""
    application = create_application()
    await application.initialize()
    await application.start()
    logger.info("Bot started in polling mode")
    
    # Start polling
    await application.updater.start_polling()
    
    # Keep running
    try:
        import asyncio
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Bot stopping...")
        await application.stop()
        await application.shutdown()
