import json
import logging
import sys
from datetime import datetime, timezone

from .config import get_settings

settings = get_settings()

metrics = None

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "environment": settings.ENVIRONMENT,
                "logger": record.name,
                "message": record.getMessage(),
            },
            ensure_ascii=False,
        )


def get_logger() -> logging.Logger:
    logger_name = settings.ENVIRONMENT.lower()

    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    if settings.LOGGER_LEVEL:
        level = settings.LOGGER_LEVEL.upper()
    elif logger_name == "development":
        level = "DEBUG"
    else:
        level = "INFO"

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)
    logger.propagate = False

    return logger
