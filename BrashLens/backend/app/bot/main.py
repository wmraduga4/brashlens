"""Entry point for Telegram bot service."""
import asyncio
import logging
from app.bot.bot import setup_webhook, start_polling
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to start the bot."""
    logger.info("Starting BrashLens Telegram bot...")
    
    try:
        # Проверяем что WEBHOOK_URL не пустой и не None
        if settings.WEBHOOK_URL and settings.WEBHOOK_URL.strip():
            logger.info(f"Starting bot in webhook mode: {settings.WEBHOOK_URL}")
            await setup_webhook(settings.WEBHOOK_URL)
        else:
            logger.info("Starting bot in polling mode...")
            await start_polling()
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
