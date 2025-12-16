"""Конфигурация Telegram бота."""
from app.core.config import settings

# Токен бота из настроек
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN

# Webhook URL (если нужен для production)
WEBHOOK_URL = settings.WEBHOOK_URL
