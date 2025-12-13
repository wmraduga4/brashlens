"""Telegram webhook endpoint."""
from fastapi import APIRouter, Request, status
from fastapi.responses import Response
from telegram import Update
from telegram.error import TelegramError

from app.bot.bot import get_application
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Telegram webhook",
    description="Endpoint для получения обновлений от Telegram Bot API через webhook.",
    response_class=Response,
    responses={
        200: {
            "description": "Обновление успешно обработано",
        },
        400: {
            "description": "Неверный формат данных",
        },
        500: {
            "description": "Ошибка обработки обновления",
        },
    },
)
async def telegram_webhook(request: Request) -> Response:
    """
    Обработка webhook запросов от Telegram.
    
    Args:
        request: FastAPI Request объект с телом запроса
        
    Returns:
        Response: HTTP 200 OK если успешно обработано
    """
    try:
        # Парсим Update из JSON
        update_data = await request.json()
        update = Update.de_json(update_data, None)
        
        if update is None:
            logger.warning("Received invalid update from Telegram")
            return Response(status_code=status.HTTP_200_OK)  # Всегда 200 для Telegram
        
        # Получаем Application и обрабатываем обновление
        application = await get_application()
        await application.process_update(update)
        
        logger.debug(f"Processed update {update.update_id}")
        return Response(status_code=status.HTTP_200_OK)
        
    except TelegramError as e:
        logger.error(f"Telegram error processing webhook: {e}")
        return Response(status_code=status.HTTP_200_OK)  # Всегда возвращаем 200 для Telegram
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return Response(status_code=status.HTTP_200_OK)  # Всегда возвращаем 200 для Telegram
