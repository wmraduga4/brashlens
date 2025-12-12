"""Centralized logging configuration."""
import logging
import sys
from logging.config import dictConfig
from typing import Any

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
        "detailed": {
            "formatter": "detailed",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "app": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "celery": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}


def setup_logging() -> None:
    """Настроить логирование для приложения."""
    dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """
    Получить logger с указанным именем.
    
    Args:
        name: Имя logger (обычно __name__)
        
    Returns:
        logging.Logger: Настроенный logger
    """
    return logging.getLogger(name)
