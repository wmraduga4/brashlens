"""Telegram bot handlers."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    keyboard = [
        [
            InlineKeyboardButton("📸 Я фотограф", callback_data="role_photographer"),
            InlineKeyboardButton("👤 Я клиент", callback_data="role_client"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я BrashLens бот.",
        reply_markup=reply_markup
    )
    logger.info(f"User {update.effective_user.id} sent /start command")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries from inline buttons."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "role_photographer":
        await query.edit_message_text("📸 Отлично! Вы выбрали роль фотографа.")
        logger.info(f"User {update.effective_user.id} selected photographer role")
    elif query.data == "role_client":
        await query.edit_message_text("👤 Отлично! Вы выбрали роль клиента.")
        logger.info(f"User {update.effective_user.id} selected client role")
    else:
        await query.edit_message_text("Неизвестная команда.")
