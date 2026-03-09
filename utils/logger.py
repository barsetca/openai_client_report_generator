"""Настройка логирования для приложения."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Загружаем .env из корня проекта
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

LOG_LEVEL_NAMES = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def setup_logging(level: int | None = None) -> None:
    """
    Настраивает логирование для всех модулей.
    
    Уровень берётся из .env: LOG_LEVEL (DEBUG, INFO, WARNING, ERROR).
    По умолчанию: INFO.
    
    Args:
        level: Явно заданный уровень (если None — читается из .env).
    """
    if level is None:
        env_level = os.getenv("LOG_LEVEL", "info").strip().lower()
        level = LOG_LEVEL_NAMES.get(env_level, logging.INFO)
    
    # force=True — переконфигурировать даже если логирование уже настроено
    logging.basicConfig(
        level=level,
        force=True,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Уменьшаем уровень для сторонних библиотек
    for name in ("httpx", "httpcore", "openai", "aiogram", "fontTools", "fontTools.ttLib", "fontTools.subset"):
        logging.getLogger(name).setLevel(logging.WARNING)
