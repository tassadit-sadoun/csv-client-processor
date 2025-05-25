import logging
import sys
from typing import Optional

LOGGING_FORMATTER = (
    "%(asctime)s [%(funcName)s] [%(filename)s:%(lineno)d]"
    " %(levelname)-5s - %(message)s"
)

DebugLevels = ["DEBUG", "INFO", "WARNING", "ERROR"]
DebugLevelType = str


def get_logger(
    name: Optional[str] = None, level: DebugLevelType = "DEBUG"
) -> logging.Logger:
    logger = logging.getLogger(name=name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOGGING_FORMATTER)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if not level or level not in DebugLevels:
        logger.warning(
            "Invalid logging level %s. Setting logging level to DEBUG.", level
        )
        level = "DEBUG"

    logger.setLevel(level=level)
    return logger
