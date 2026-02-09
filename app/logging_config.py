"""Configure logging from .env LOG_LEVEL."""

import logging

from app.config import get_settings

VALID_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def configure_logging() -> None:
    """Set up root logger with level from LOG_LEVEL env var."""
    settings = get_settings()
    level_name = (settings.log_level or "INFO").upper()
    if level_name not in VALID_LEVELS:
        level_name = "INFO"
    level = getattr(logging, level_name)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Reduce noise from third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
