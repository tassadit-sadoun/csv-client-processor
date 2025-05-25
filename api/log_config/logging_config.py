LOGGING_FORMATTER = (
    "%(asctime)s [%(funcName)s] [%(filename)s:%(lineno)d]"
    " %(levelname)-5s - %(message)s"
)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": LOGGING_FORMATTER,
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "DEBUG",
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
