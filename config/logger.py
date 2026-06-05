# config/logger.py
# ============================================================
# Centralised logger using loguru.
# Import `logger` from this module everywhere in the project.
# ============================================================

import sys
import os
from loguru import logger
from config.settings import settings


def setup_logger():
    """Configure loguru with console + rotating file output."""
    os.makedirs(settings.log_dir, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Console — coloured, human-readable
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # Rotating file — full detail
    logger.add(
        os.path.join(settings.log_dir, "platform_{time:YYYY-MM-DD}.log"),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",      # New file every midnight
        retention="14 days",   # Keep 2 weeks
        compression="zip",
        enqueue=True,          # Thread-safe
    )

    return logger


# Initialise on import
setup_logger()

__all__ = ["logger"]
