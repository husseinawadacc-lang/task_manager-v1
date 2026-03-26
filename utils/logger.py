"""
Logger Utility
==============

Centralized logging configuration for the application.

Features
--------
✔ Request ID support (for tracing requests)
✔ Clean and consistent log format
✔ Reusable across all modules
✔ Safe initialization (no duplicate handlers)
"""

import logging
from utils.request_context import request_id_ctx


class RequestIDFilter(logging.Filter):
    """
    Inject request_id into every log record.
    """

    def filter(self, record):
        record.request_id = request_id_ctx.get() or "N/A"
        return True


def get_logger(name: str) -> logging.Logger:
    """
    Create or retrieve a configured logger.

    Ensures:
    - No duplicate handlers
    - Request ID included in logs
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if not logger.handlers:

        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [req:%(request_id)s] [%(name)s] %(message)s"
        )

        handler.setFormatter(formatter)

        # Add request id filter
        handler.addFilter(RequestIDFilter())

        logger.addHandler(handler)

        logger.setLevel(logging.INFO)

    return logger