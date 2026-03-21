# logging_config.py
"""
Shared structured JSON logging configuration for Teleoscope backend services.

Usage:
    from backend.logging_config import configure_logging
    configure_logging(service="worker-tasks")

Each log record is emitted as a single-line JSON object with the fields:
    timestamp  – ISO 8601 with milliseconds and Z suffix
    level      – log level name (e.g. "INFO", "ERROR")
    logger     – logger name (e.g. "backend.tasks")
    service    – the service label passed to configure_logging()
    message    – the formatted log message
    exc_info   – (optional) formatted traceback string, present only when an
                 exception is attached to the record
"""

import json
import logging
import traceback
from datetime import datetime, timezone


class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object."""

    def __init__(self, service: str) -> None:
        super().__init__()
        self._service = service

    def format(self, record: logging.LogRecord) -> str:
        # Build the timestamp in ISO 8601 format with millisecond precision and Z suffix.
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc)
        timestamp = ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"

        payload: dict = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "service": self._service,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        elif record.exc_text:
            payload["exc_info"] = record.exc_text

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(
    service: str,
    level: int = logging.INFO,
) -> None:
    """Configure the root logger to emit structured JSON log lines.

    Args:
        service: A short label added to every log record as the ``service``
                 field (e.g. ``"worker-tasks"``).
        level:   Logging level for the root logger.  Defaults to
                 ``logging.INFO``.

    The function is idempotent: it removes all existing handlers from the
    root logger before installing the JSON handler, so calling it more than
    once is safe.
    """
    root = logging.getLogger()

    # Remove any handlers that were added before this call (e.g. by a
    # previous basicConfig() call or by an imported library).
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()

    handler = logging.StreamHandler()
    handler.setFormatter(_JSONFormatter(service=service))

    root.setLevel(level)
    root.addHandler(handler)
