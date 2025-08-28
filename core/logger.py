import os
import sys
from pathlib import Path
from loguru import logger
import logging
from functools import wraps
import time

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
    filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR"] and not record["message"].startswith("Processing")
)

logger.add(
    "logs/application.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="50 MB",
    retention="3 days",
    compression=None,
    backtrace=True,
    diagnose=True,
    enqueue=True,
    filter=lambda record: record["name"].startswith(("agents.", "core.", "utils.", "graph", "streamlit_app", "main"))
)

logger.add(
    "logs/errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="7 days",
    compression=None,
    backtrace=True,
    diagnose=True,
    enqueue=True,
    filter=lambda record: record["name"].startswith(("agents.", "core.", "utils.", "graph", "streamlit_app", "main"))
)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        if record.name.startswith(("agents.", "core.", "utils.", "graph", "streamlit_app", "main")):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

logger.info("Logging system initialized")
