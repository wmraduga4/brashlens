"""Telegram bot setup and configuration."""
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from app.bot.handlers import start_command, handle_callback
from app.core.config import settings


def create_application() -> Application:
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Регистрация handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    return application


async def setup_webhook(webhook_url: str) -> None:
    """Setup webhook for the bot."""
    application = create_application()
    await application.initialize()
    await application.bot.set_webhook(webhook_url)
    await application.start()
    print(f"Webhook set to: {webhook_url}")
    # Keep running
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=8443,
        webhook_url=webhook_url
    )


async def start_polling() -> None:
    """Start bot in polling mode."""
    application = create_application()
    await application.initialize()
    await application.start()
    print("Bot started in polling mode")
    
    # Start polling
    await application.updater.start_polling()
    
    # Keep running
    try:
        import asyncio
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await application.stop()
        await application.shutdown()
