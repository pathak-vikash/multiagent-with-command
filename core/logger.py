"""
Centralized logging configuration using loguru.
"""

import os
import sys
from pathlib import Path
from loguru import logger
import logging

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Remove default logger
logger.remove()

# Add console logger with color
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# Add file logger for application logs (INFO and above)
logger.add(
    "logs/application.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    rotation="100 MB",
    retention="7 days",
    compression=None,
    backtrace=True,
    diagnose=True,
    enqueue=True,
    filter=lambda record: record["name"].startswith(("agents.", "core.", "utils.", "graph", "streamlit_app", "main"))  # Only log our application modules
)

# Add error file logger for errors only
logger.add(
    "logs/errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression=None,
    backtrace=True,
    diagnose=True,
    enqueue=True,
    filter=lambda record: record["name"].startswith(("agents.", "core.", "utils.", "graph", "streamlit_app", "main"))  # Only log our application modules
)

# Intercept standard logging and redirect to loguru (but only for our application)
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Skip system logging events and only process our application logs
        if record.name.startswith(("agents.", "core.", "utils.", "graph", "streamlit_app", "main")):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Setup standard logging to use loguru (but only for our application modules)
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

logger.info("Logging system initialized")
