import logging
import sys

import structlog


def configure_logging(level: str = "INFO") -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    pre_chain = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            *pre_chain,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    return structlog.get_logger(name)
