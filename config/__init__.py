# config/__init__.py
from config.settings import settings, get_settings
from config.logger import logger

__all__ = ["settings", "get_settings", "logger"]
