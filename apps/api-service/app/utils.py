import json
import logging
import sys
from datetime import datetime, timezone

# 62 characters: digits (0-9), lowercase (a-z), uppercase (A-Z)
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base62(num: int) -> str:
    """Encodes a non-negative integer into a base62 string representation."""
    if num == 0:
        return BASE62_ALPHABET[0]
    result = []
    base = len(BASE62_ALPHABET)
    while num > 0:
        result.append(BASE62_ALPHABET[num % base])
        num //= base
    return "".join(reversed(result))


class StructuredJSONFormatter(logging.Formatter):
    """Formats log records as structured single-line JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include custom extra properties if provided via extra={"extra_fields": {...}}
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log_payload.update(record.extra_fields)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


def setup_json_logging(level: str = "INFO"):
    """Configures the root logger to output structured JSON to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    # Replace existing handlers to ensure single JSON output
    root_logger.handlers = [handler]
